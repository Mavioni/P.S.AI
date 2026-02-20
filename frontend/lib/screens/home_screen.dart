import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/dialogue_state.dart';
import '../widgets/persona_grid.dart';
import '../widgets/question_input.dart';
import 'agora_screen.dart';

/// Landing page — the courtyard before the Agora.
/// Users select personas and pose a question.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DialogueState>().loadPersonas();
    });
  }

  void _onSubmit(String question) async {
    final state = context.read<DialogueState>();
    await state.startDialogue(question);

    if (!mounted) return;

    if (state.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.error!)),
      );
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const AgoraScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<DialogueState>();
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // ── Header ───────────────────────────────────────
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(32, 48, 32, 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'P.S.AI',
                      style: theme.textTheme.headlineLarge?.copyWith(
                        letterSpacing: 4,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'POSTHUMOUS SOCIAL ARTIFICIAL INTELLIGENCE',
                      style: theme.textTheme.labelSmall?.copyWith(
                        letterSpacing: 2.5,
                      ),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Summon the great minds of history into dialogue.',
                      style: theme.textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Select one thinker for a private audience, or '
                      'two or more for a Symposium.',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),

            const SliverToBoxAdapter(child: SizedBox(height: 24)),

            // ── Mode indicator ───────────────────────────────
            if (state.selectedPersonaIds.isNotEmpty)
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32),
                  child: Row(
                    children: [
                      Icon(
                        state.mode == 'symposium'
                            ? Icons.groups
                            : Icons.person,
                        color: theme.colorScheme.primary,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        state.mode == 'symposium'
                            ? 'SYMPOSIUM MODE'
                            : 'SINGLE DIALOGUE',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${state.selectedPersonaIds.length} selected',
                        style: theme.textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
              ),

            const SliverToBoxAdapter(child: SizedBox(height: 16)),

            // ── Persona grid ─────────────────────────────────
            if (state.loadingPersonas)
              const SliverToBoxAdapter(
                child: Center(
                  child: Padding(
                    padding: EdgeInsets.all(48),
                    child: CircularProgressIndicator(),
                  ),
                ),
              )
            else
              SliverToBoxAdapter(
                child: PersonaGrid(
                  personas: state.personas,
                  selectedIds: state.selectedPersonaIds,
                  onToggle: state.togglePersona,
                ),
              ),

            const SliverToBoxAdapter(child: SizedBox(height: 32)),

            // ── Question input ───────────────────────────────
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: QuestionInput(
                  enabled: state.selectedPersonaIds.isNotEmpty &&
                      !state.loading,
                  loading: state.loading,
                  onSubmit: _onSubmit,
                ),
              ),
            ),

            const SliverToBoxAdapter(child: SizedBox(height: 48)),
          ],
        ),
      ),
    );
  }
}
