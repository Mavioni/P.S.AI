import 'package:flutter/foundation.dart';
import '../models/persona.dart';
import 'api_client.dart';

/// Application state for persona selection and dialogue management.
class DialogueState extends ChangeNotifier {
  final ApiClient _api;

  DialogueState(this._api);

  // ── Personas ─────────────────────────────────────────────────

  List<PersonaSummary> _personas = [];
  List<PersonaSummary> get personas => _personas;

  bool _loadingPersonas = false;
  bool get loadingPersonas => _loadingPersonas;

  final Set<String> _selectedPersonaIds = {};
  Set<String> get selectedPersonaIds => _selectedPersonaIds;

  Future<void> loadPersonas() async {
    _loadingPersonas = true;
    notifyListeners();
    try {
      _personas = await _api.listPersonas();
    } catch (e) {
      print('Failed to load personas: $e');
    } finally {
      _loadingPersonas = false;
      notifyListeners();
    }
  }

  void togglePersona(String id) {
    if (_selectedPersonaIds.contains(id)) {
      _selectedPersonaIds.remove(id);
    } else {
      _selectedPersonaIds.add(id);
    }
    notifyListeners();
  }

  void clearSelection() {
    _selectedPersonaIds.clear();
    notifyListeners();
  }

  // ── Dialogue ─────────────────────────────────────────────────

  DialogueResponse? _currentDialogue;
  DialogueResponse? get currentDialogue => _currentDialogue;

  bool _loading = false;
  bool get loading => _loading;

  String? _error;
  String? get error => _error;

  String get mode =>
      _selectedPersonaIds.length >= 2 ? 'symposium' : 'single';

  Future<void> startDialogue(String question) async {
    if (_selectedPersonaIds.isEmpty) return;

    _loading = true;
    _error = null;
    _currentDialogue = null;
    notifyListeners();

    try {
      _currentDialogue = await _api.startDialogue(
        question: question,
        personaIds: _selectedPersonaIds.toList(),
        mode: mode,
      );
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> continueDialogue(String userInput) async {
    if (_currentDialogue == null) return;

    _loading = true;
    _error = null;
    notifyListeners();

    try {
      _currentDialogue = await _api.continueDialogue(
        sessionId: _currentDialogue!.sessionId,
        userInput: userInput,
      );
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  void resetDialogue() {
    _currentDialogue = null;
    _error = null;
    notifyListeners();
  }
}
