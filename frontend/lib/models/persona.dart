/// Data models mirroring the backend Pydantic schemas.

class PersonaSummary {
  final String id;
  final String fullName;
  final int? birthYear;
  final int? deathYear;
  final String nationality;
  final String primaryLanguage;
  final List<String> domains;
  final String tagline;

  const PersonaSummary({
    required this.id,
    required this.fullName,
    this.birthYear,
    this.deathYear,
    this.nationality = '',
    this.primaryLanguage = '',
    this.domains = const [],
    this.tagline = '',
  });

  factory PersonaSummary.fromJson(Map<String, dynamic> json) {
    return PersonaSummary(
      id: json['id'] as String,
      fullName: json['full_name'] as String,
      birthYear: json['birth_year'] as int?,
      deathYear: json['death_year'] as int?,
      nationality: json['nationality'] as String? ?? '',
      primaryLanguage: json['primary_language'] as String? ?? '',
      domains: (json['domains'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      tagline: json['tagline'] as String? ?? '',
    );
  }
}

class DialogueTurn {
  final int turnNumber;
  final String role;
  final String? personaId;
  final String? personaName;
  final String content;

  const DialogueTurn({
    required this.turnNumber,
    required this.role,
    this.personaId,
    this.personaName,
    required this.content,
  });

  factory DialogueTurn.fromJson(Map<String, dynamic> json) {
    return DialogueTurn(
      turnNumber: json['turn_number'] as int,
      role: json['role'] as String,
      personaId: json['persona_id'] as String?,
      personaName: json['persona_name'] as String?,
      content: json['content'] as String,
    );
  }
}

class DialogueResponse {
  final String sessionId;
  final String question;
  final String mode;
  final List<DialogueTurn> turns;
  final bool isComplete;

  const DialogueResponse({
    required this.sessionId,
    required this.question,
    required this.mode,
    required this.turns,
    required this.isComplete,
  });

  factory DialogueResponse.fromJson(Map<String, dynamic> json) {
    return DialogueResponse(
      sessionId: json['session_id'] as String,
      question: json['question'] as String,
      mode: json['mode'] as String,
      turns: (json['turns'] as List<dynamic>)
          .map((e) => DialogueTurn.fromJson(e as Map<String, dynamic>))
          .toList(),
      isComplete: json['is_complete'] as bool,
    );
  }
}
