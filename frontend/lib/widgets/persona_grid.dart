import 'package:flutter/material.dart';
import '../models/persona.dart';
import 'persona_card.dart';

/// Responsive grid layout for persona selection.
class PersonaGrid extends StatelessWidget {
  final List<PersonaSummary> personas;
  final Set<String> selectedIds;
  final void Function(String) onToggle;

  const PersonaGrid({
    super.key,
    required this.personas,
    required this.selectedIds,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final crossAxisCount = constraints.maxWidth > 900
              ? 4
              : constraints.maxWidth > 600
                  ? 3
                  : 2;

          return GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 0.85,
            ),
            itemCount: personas.length,
            itemBuilder: (context, index) {
              final persona = personas[index];
              return PersonaCard(
                persona: persona,
                isSelected: selectedIds.contains(persona.id),
                onTap: () => onToggle(persona.id),
              );
            },
          );
        },
      ),
    );
  }
}
