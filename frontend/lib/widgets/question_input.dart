import 'package:flutter/material.dart';

/// Text field + submit button for posing questions to the personas.
class QuestionInput extends StatefulWidget {
  final bool enabled;
  final bool loading;
  final String hintText;
  final void Function(String) onSubmit;

  const QuestionInput({
    super.key,
    required this.enabled,
    required this.loading,
    this.hintText = 'Pose a question to the assembled thinkers...',
    required this.onSubmit,
  });

  @override
  State<QuestionInput> createState() => _QuestionInputState();
}

class _QuestionInputState extends State<QuestionInput> {
  final _controller = TextEditingController();

  void _submit() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    widget.onSubmit(text);
    _controller.clear();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _controller,
            enabled: widget.enabled,
            maxLines: null,
            minLines: 1,
            textInputAction: TextInputAction.send,
            onSubmitted: (_) => _submit(),
            decoration: InputDecoration(
              hintText: widget.hintText,
            ),
          ),
        ),
        const SizedBox(width: 12),
        widget.loading
            ? const SizedBox(
                width: 48,
                height: 48,
                child: Padding(
                  padding: EdgeInsets.all(12),
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              )
            : IconButton.filled(
                onPressed: widget.enabled ? _submit : null,
                icon: const Icon(Icons.send),
                tooltip: 'Submit',
              ),
      ],
    );
  }
}
