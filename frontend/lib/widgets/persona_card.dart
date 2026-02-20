import 'package:flutter/material.dart';
import '../models/persona.dart';

/// A selectable card representing a single historical persona.
class PersonaCard extends StatelessWidget {
  final PersonaSummary persona;
  final bool isSelected;
  final VoidCallback onTap;

  const PersonaCard({
    super.key,
    required this.persona,
    required this.isSelected,
    required this.onTap,
  });

  /// Map persona IDs to representative icons.
  IconData get _icon {
    switch (persona.id) {
      case 'socrates':
        return Icons.balance;
      case 'kant':
        return Icons.auto_stories;
      case 'hypatia':
        return Icons.science;
      case 'marx':
        return Icons.handshake;
      case 'simone_de_beauvoir':
        return Icons.diversity_3;
      default:
        return Icons.person;
    }
  }

  String _formatYears() {
    if (persona.birthYear == null || persona.deathYear == null) return '';
    String fmt(int y) => y < 0 ? '${-y} BCE' : '$y';
    return '${fmt(persona.birthYear!)} – ${fmt(persona.deathYear!)}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        decoration: BoxDecoration(
          color: isSelected
              ? cs.primary.withValues(alpha: 0.08)
              : cs.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? cs.primary : cs.outline.withValues(alpha: 0.3),
            width: isSelected ? 1.5 : 0.5,
          ),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon + selection indicator
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: isSelected
                      ? cs.primary.withValues(alpha: 0.2)
                      : cs.surfaceContainerHighest,
                  child: Icon(_icon, color: cs.primary, size: 22),
                ),
                if (isSelected)
                  Icon(Icons.check_circle, color: cs.primary, size: 20),
              ],
            ),
            const Spacer(),

            // Name
            Text(
              persona.fullName,
              style: theme.textTheme.titleMedium,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),

            // Years
            if (_formatYears().isNotEmpty)
              Text(
                _formatYears(),
                style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
              ),
            const SizedBox(height: 6),

            // Domains
            Wrap(
              spacing: 4,
              runSpacing: 2,
              children: persona.domains.take(3).map((d) {
                return Text(
                  d,
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: cs.secondary,
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}
