"""RDF knowledge graph management — SPARQL queries over persona belief graphs.

Uses rdflib for graph loading and querying. Supports:
  - Belief retrieval by persona
  - Contradiction detection via psai:contradicts
  - Domain expertise scoring
  - Epistemic friction calculation between persona pairs
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

PSAI = Namespace("http://psai.local/ontology#")


class KnowledgeGraphManager:
    """Manages RDF knowledge graphs for all loaded personas."""

    def __init__(self) -> None:
        self._graph = Graph()
        self._graph.bind("psai", PSAI)

    def load_schema(self, schema_path: Path) -> None:
        """Load the core ontology schema."""
        if schema_path.exists():
            self._graph.parse(str(schema_path), format="turtle")

    def load_persona_graph(self, ttl_path: Path) -> None:
        """Load a persona's knowledge graph TTL file."""
        if ttl_path.exists():
            try:
                self._graph.parse(str(ttl_path), format="turtle")
            except Exception as exc:
                print(f"[P.S.AI] WARNING: Failed to parse {ttl_path.name}: {exc}")

    def load_all(self, ontology_root: Path) -> None:
        """Load schema and all persona knowledge graphs."""
        schema_path = ontology_root / "schemas" / "persona.ttl"
        self.load_schema(schema_path)

        personas_dir = ontology_root / "personas"
        if personas_dir.is_dir():
            for ttl_path in personas_dir.glob("*.ttl"):
                self.load_persona_graph(ttl_path)

    def get_beliefs(self, persona_id: str) -> list[dict[str, str]]:
        """Query all beliefs for a persona via SPARQL."""
        query = """
        SELECT ?proposition ?confidence WHERE {
            ?persona psai:hasEpistemicProfile ?profile .
            ?profile psai:holdsBelief ?belief .
            ?belief psai:proposition ?proposition .
            OPTIONAL { ?belief psai:confidence ?confidence }
            FILTER(CONTAINS(STR(?persona), "%s"))
        }
        """ % persona_id

        results = []
        for row in self._graph.query(query, initNs={"psai": PSAI}):
            results.append({
                "proposition": str(row.proposition),
                "confidence": str(row.confidence) if row.confidence else "0.9",
            })
        return results

    def find_contradictions(self, persona_a: str, persona_b: str) -> list[dict]:
        """Find beliefs that are marked as contradicting between two personas."""
        query = """
        SELECT ?belief_a ?belief_b ?prop_a ?prop_b WHERE {
            ?pa psai:hasEpistemicProfile ?profile_a .
            ?profile_a psai:holdsBelief ?belief_a .
            ?belief_a psai:proposition ?prop_a .
            ?belief_a psai:contradicts ?belief_b .
            ?pb psai:hasEpistemicProfile ?profile_b .
            ?profile_b psai:holdsBelief ?belief_b .
            ?belief_b psai:proposition ?prop_b .
            FILTER(CONTAINS(STR(?pa), "%s"))
            FILTER(CONTAINS(STR(?pb), "%s"))
        }
        """ % (persona_a, persona_b)

        results = []
        for row in self._graph.query(query, initNs={"psai": PSAI}):
            results.append({
                "persona_a_belief": str(row.prop_a),
                "persona_b_belief": str(row.prop_b),
            })
        return results

    def compute_domain_scores(
        self, question_domains: list[str]
    ) -> dict[str, float]:
        """Score each persona's relevance to the given question domains.

        Returns {persona_id: score} where score is in [0.0, 1.0].
        """
        query = """
        SELECT ?persona ?domain WHERE {
            ?persona a psai:Persona .
            ?persona psai:hasEpistemicProfile ?profile .
            ?profile psai:engagesDomain ?domain .
        }
        """

        persona_domains: dict[str, set[str]] = {}
        for row in self._graph.query(query, initNs={"psai": PSAI}):
            pid = str(row.persona).split("#")[-1].removeprefix("persona_")
            domain = str(row.domain).lower()
            persona_domains.setdefault(pid, set()).add(domain)

        question_set = {d.lower() for d in question_domains}
        scores: dict[str, float] = {}
        for pid, domains in persona_domains.items():
            if not question_set:
                scores[pid] = 0.5
            else:
                overlap = len(domains & question_set)
                scores[pid] = min(1.0, overlap / len(question_set))

        return scores

    def compute_friction_matrix(self) -> dict[tuple[str, str], float]:
        """Compute pairwise epistemic friction between all personas.

        Friction is based on the presence of psai:contradicts relationships
        and domain divergence. Returns {(id_a, id_b): friction_score}.
        """
        # Get all persona IDs
        query = "SELECT DISTINCT ?persona WHERE { ?persona a psai:Persona }"
        persona_ids = []
        for row in self._graph.query(query, initNs={"psai": PSAI}):
            pid = str(row.persona).split("#")[-1].removeprefix("persona_")
            persona_ids.append(pid)

        matrix: dict[tuple[str, str], float] = {}
        for i, a in enumerate(persona_ids):
            for b in persona_ids[i + 1:]:
                contradictions = self.find_contradictions(a, b)
                # Base friction from contradictions
                friction = min(1.0, len(contradictions) * 0.3)
                # Add baseline friction for different personas
                friction = max(friction, 0.2)
                matrix[(a, b)] = friction
                matrix[(b, a)] = friction

        return matrix

    @property
    def triple_count(self) -> int:
        return len(self._graph)
