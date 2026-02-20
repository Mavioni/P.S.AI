import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/dialogue_state.dart';
import '../widgets/dialogue_turn_card.dart';
import '../widgets/question_input.dart';

/// The Agora — where the dialogue takes place.
class AgoraScreen extends StatelessWidget {
  const AgoraScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<DialogueState>();
    final dialogue = state.currentDialogue;
    final theme = Theme.of(context);

    if (dialogue == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Agora')),
        body: const Center(child: Text('No active dialogue.')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(
              dialogue.mode == 'symposium' ? Icons.groups : Icons.person,
              size: 20,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(width: 8),
            Text(
              dialogue.mode == 'symposium' ? 'Symposium' : 'Dialogue',
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'New dialogue',
            onPressed: () {
              state.resetDialogue();
              Navigator.of(context).pop();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Question banner ──────────────────────────────
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            color: theme.colorScheme.surface,
            child: Text(
              '"${dialogue.question}"',
              style: theme.textTheme.headlineMedium?.copyWith(
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
          const Divider(height: 1),

          // ── Turns ────────────────────────────────────────
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: dialogue.turns.length,
              itemBuilder: (context, index) {
                final turn = dialogue.turns[index];
                return DialogueTurnCard(turn: turn);
              },
            ),
          ),

          // ── Loading indicator ────────────────────────────
          if (state.loading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: LinearProgressIndicator(),
            ),

          // ── Continue input (single mode only) ────────────
          if (dialogue.mode == 'single' && !dialogue.isComplete)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: QuestionInput(
                enabled: !state.loading,
                loading: state.loading,
                hintText: 'Continue the dialogue...',
                onSubmit: (input) => state.continueDialogue(input),
              ),
            ),
        ],
      ),
    );
  }
}
