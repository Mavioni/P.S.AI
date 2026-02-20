import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/persona.dart';

/// HTTP client for the P.S.AI backend REST API.
class ApiClient {
  final String baseUrl;
  final http.Client _http;

  ApiClient({this.baseUrl = 'http://localhost:8000/api'})
      : _http = http.Client();

  // ── Personas ─────────────────────────────────────────────────

  Future<List<PersonaSummary>> listPersonas() async {
    final resp = await _http.get(Uri.parse('$baseUrl/personas'));
    _checkResponse(resp);
    final List<dynamic> data = jsonDecode(resp.body);
    return data.map((e) => PersonaSummary.fromJson(e)).toList();
  }

  // ── Dialogue ─────────────────────────────────────────────────

  Future<DialogueResponse> startDialogue({
    required String question,
    required List<String> personaIds,
    required String mode,
    int? maxTurns,
  }) async {
    final body = {
      'question': question,
      'persona_ids': personaIds,
      'mode': mode,
      if (maxTurns != null) 'max_turns': maxTurns,
    };
    final resp = await _http.post(
      Uri.parse('$baseUrl/dialogue'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );
    _checkResponse(resp);
    return DialogueResponse.fromJson(jsonDecode(resp.body));
  }

  Future<DialogueResponse> continueDialogue({
    required String sessionId,
    required String userInput,
  }) async {
    final resp = await _http.post(
      Uri.parse('$baseUrl/dialogue/$sessionId/continue'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_input': userInput}),
    );
    _checkResponse(resp);
    return DialogueResponse.fromJson(jsonDecode(resp.body));
  }

  Future<DialogueResponse> getDialogue(String sessionId) async {
    final resp = await _http.get(Uri.parse('$baseUrl/dialogue/$sessionId'));
    _checkResponse(resp);
    return DialogueResponse.fromJson(jsonDecode(resp.body));
  }

  // ── Health ───────────────────────────────────────────────────

  Future<Map<String, dynamic>> healthCheck() async {
    final resp = await _http.get(Uri.parse('$baseUrl/health'));
    _checkResponse(resp);
    return jsonDecode(resp.body);
  }

  void _checkResponse(http.Response resp) {
    if (resp.statusCode >= 400) {
      throw ApiException(resp.statusCode, resp.body);
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String body;
  ApiException(this.statusCode, this.body);

  @override
  String toString() => 'ApiException($statusCode): $body';
}
