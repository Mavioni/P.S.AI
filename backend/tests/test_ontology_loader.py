"""Tests for the ontology loader — verifying persona JSON-LD parsing."""

from pathlib import Path

from app.services.ontology_loader import OntologyLoader

ONTOLOGY_ROOT = Path(__file__).resolve().parents[2] / "ontology"


def test_load_all_personas():
    """All bundled persona files should parse without error."""
    loader = OntologyLoader(ONTOLOGY_ROOT)
    personas = loader.load_all()
    assert len(personas) >= 20, f"Expected at least 20 personas, got {len(personas)}"


def test_socrates_profile():
    """Verify Socrates' epistemic profile is correctly hydrated."""
    loader = OntologyLoader(ONTOLOGY_ROOT)
    loader.load_all()
    socrates = loader.get("socrates")
    assert socrates is not None
    assert socrates.full_name == "Socrates of Athens"
    assert socrates.birth_year == -470
    ep = socrates.epistemic_profile
    assert len(ep.beliefs) >= 3
    assert len(ep.methodologies) >= 1
    assert ep.rhetorical_style is not None
    assert "Elenchus" in ep.methodologies[0].name


def test_persona_domains():
    """Each persona should have at least one domain."""
    loader = OntologyLoader(ONTOLOGY_ROOT)
    personas = loader.load_all()
    for pid, persona in personas.items():
        assert len(persona.domains) >= 1, f"{pid} has no domains"


def test_prompt_assembly_integration():
    """Verify the prompt assembler can consume loaded personas."""
    from app.services.prompt_assembler import PromptAssembler

    loader = OntologyLoader(ONTOLOGY_ROOT)
    loader.load_all()
    kant = loader.get("kant")
    assert kant is not None

    system_prompt = PromptAssembler.build_system_prompt(kant)
    assert "Immanuel Kant" in system_prompt
    assert "categorical imperative" in system_prompt.lower()
    assert len(system_prompt) > 500
