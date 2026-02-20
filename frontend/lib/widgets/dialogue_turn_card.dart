import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/persona.dart';

/// Renders a single turn in the dialogue.
class DialogueTurnCard extends StatelessWidget {
  final DialogueTurn turn;

  const DialogueTurnCard({super.key, required this.turn});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    final isUser = turn.role == 'user';
    final isModerator = turn.role == 'moderator';

    final alignment =
        isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start;

    final bgColor = isUser
        ? cs.primary.withValues(alpha: 0.1)
        : isModerator
            ? cs.tertiary.withValues(alpha: 0.1)
            : cs.surface;

    final borderColor = isUser
        ? cs.primary.withValues(alpha: 0.3)
        : isModerator
            ? cs.tertiary.withValues(alpha: 0.3)
            : cs.outline.withValues(alpha: 0.2);

    final label = isUser
        ? 'You'
        : isModerator
            ? 'Moderator — Synthesis'
            : turn.personaName ?? turn.personaId ?? 'Persona';

    final labelColor = isUser
        ? cs.primary
        : isModerator
            ? cs.tertiary
            : cs.secondary;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: alignment,
        children: [
          // Speaker label
          Padding(
            padding: const EdgeInsets.only(bottom: 4, left: 4, right: 4),
            child: Text(
              label.toUpperCase(),
              style: theme.textTheme.labelSmall?.copyWith(
                color: labelColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),

          // Content bubble
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: borderColor, width: 0.5),
            ),
            child: MarkdownBody(
              data: turn.content,
              styleSheet: MarkdownStyleSheet(
                p: theme.textTheme.bodyLarge,
                strong: theme.textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                em: theme.textTheme.bodyLarge?.copyWith(
                  fontStyle: FontStyle.italic,
                ),
                blockquote: theme.textTheme.bodyLarge?.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.7),
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
