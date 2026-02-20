import 'dart:math';
import 'package:flutter/material.dart';

/// 3D Fibonacci sphere distribution of persona nodes with perspective projection,
/// wireframe connections, Z-depth sorting, and ambient rotation.
///
/// This is the signature visual component of the Dark Atheneum aesthetic.
class ConstellationPainter extends CustomPainter {
  final List<ConstellationNode> nodes;
  final double rotationX;
  final double rotationY;
  final double focalLength;
  final String? activeSpeakerId;
  final double pulsePhase; // 0.0 – 1.0, for 2s speaking pulse

  ConstellationPainter({
    required this.nodes,
    this.rotationX = 0.0,
    this.rotationY = 0.0,
    this.focalLength = 1000.0,
    this.activeSpeakerId,
    this.pulsePhase = 0.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;

    // Project all nodes to 2D with Z-depth
    final projected = <_ProjectedNode>[];
    for (final node in nodes) {
      final p3 = _rotate(node.x, node.y, node.z, rotationX, rotationY);
      final scale = focalLength / (focalLength + p3.z);
      final px = cx + p3.x * scale;
      final py = cy + p3.y * scale;
      projected.add(_ProjectedNode(
        id: node.id,
        label: node.label,
        x: px,
        y: py,
        z: p3.z,
        scale: scale,
        color: node.color,
        activity: node.activity,
        isSpeaking: node.id == activeSpeakerId,
      ));
    }

    // Sort by Z for painter's algorithm (far to near)
    projected.sort((a, b) => b.z.compareTo(a.z));

    // ── Draw wireframe connections ────────────────────────
    final wirePaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.06)
      ..strokeWidth = 0.5
      ..style = PaintingStyle.stroke;

    for (int i = 0; i < projected.length; i++) {
      for (int j = i + 1; j < projected.length; j++) {
        final a = projected[i];
        final b = projected[j];
        final dist = sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2));
        if (dist < 250) {
          final alpha = (1.0 - dist / 250) * 0.1;
          wirePaint.color = Colors.white.withValues(alpha: alpha);
          canvas.drawLine(Offset(a.x, a.y), Offset(b.x, b.y), wirePaint);
        }
      }
    }

    // ── Draw nodes ────────────────────────────────────────
    for (final node in projected) {
      _drawNode(canvas, node);
    }
  }

  void _drawNode(Canvas canvas, _ProjectedNode node) {
    final baseRadius = 18.0 * node.scale;
    final isSpeaking = node.isSpeaking;

    // Speaking pulse: radius oscillates between 1.0x and 1.3x
    final pulseMultiplier =
        isSpeaking ? 1.0 + 0.3 * sin(pulsePhase * 2 * pi) : 1.0;
    final radius = baseRadius * pulseMultiplier;

    // ── Outer ring ────────────────────────────────────
    final outerPaint = Paint()
      ..color = node.color.withValues(alpha: 0.3 + node.activity * 0.4)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5 * node.scale;
    canvas.drawCircle(Offset(node.x, node.y), radius, outerPaint);

    // ── Inner fill ────────────────────────────────────
    final fillPaint = Paint()
      ..color = node.color.withValues(alpha: 0.08 + node.activity * 0.12)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(node.x, node.y), radius * 0.85, fillPaint);

    // ── Core luminosity (speaking glow) ───────────────
    if (isSpeaking) {
      final glowPaint = Paint()
        ..color = node.color.withValues(alpha: 0.4 * sin(pulsePhase * 2 * pi).abs())
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 12);
      canvas.drawCircle(Offset(node.x, node.y), radius * 1.2, glowPaint);
    }

    // ── Label with glow ──────────────────────────────
    final textStyle = TextStyle(
      color: Colors.white.withValues(alpha: 0.6 + node.activity * 0.4),
      fontSize: 11 * node.scale,
      fontWeight: isSpeaking ? FontWeight.w600 : FontWeight.w400,
      shadows: isSpeaking
          ? [
              Shadow(
                color: node.color.withValues(alpha: 0.6),
                blurRadius: 5,
              ),
            ]
          : null,
    );

    final textSpan = TextSpan(text: node.label, style: textStyle);
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    )..layout();

    textPainter.paint(
      canvas,
      Offset(
        node.x - textPainter.width / 2,
        node.y + radius + 6 * node.scale,
      ),
    );
  }

  /// Rotate a 3D point around X and Y axes.
  _Vec3 _rotate(double x, double y, double z, double rx, double ry) {
    // Rotate around Y axis
    final cosY = cos(ry);
    final sinY = sin(ry);
    final x1 = x * cosY - z * sinY;
    final z1 = x * sinY + z * cosY;

    // Rotate around X axis
    final cosX = cos(rx);
    final sinX = sin(rx);
    final y1 = y * cosX - z1 * sinX;
    final z2 = y * sinX + z1 * cosX;

    return _Vec3(x1, y1, z2);
  }

  @override
  bool shouldRepaint(ConstellationPainter oldDelegate) => true;
}

/// A node in the 3D constellation (pre-rotation coordinates).
class ConstellationNode {
  final String id;
  final String label;
  final double x, y, z;
  final Color color;
  final double activity; // 0.0 – 1.0

  const ConstellationNode({
    required this.id,
    required this.label,
    required this.x,
    required this.y,
    required this.z,
    required this.color,
    this.activity = 0.5,
  });

  /// Distribute N nodes on a Fibonacci sphere of given radius.
  static List<ConstellationNode> fibonacciSphere({
    required List<String> ids,
    required List<String> labels,
    required List<Color> colors,
    double radius = 200,
  }) {
    final n = ids.length;
    final goldenRatio = (1 + sqrt(5)) / 2;
    final nodes = <ConstellationNode>[];

    for (int i = 0; i < n; i++) {
      final theta = acos(1 - 2 * (i + 0.5) / n);
      final phi = 2 * pi * i / goldenRatio;

      nodes.add(ConstellationNode(
        id: ids[i],
        label: labels[i],
        x: radius * sin(theta) * cos(phi),
        y: radius * sin(theta) * sin(phi),
        z: radius * cos(theta),
        color: colors[i % colors.length],
      ));
    }

    return nodes;
  }
}

class _Vec3 {
  final double x, y, z;
  const _Vec3(this.x, this.y, this.z);
}

class _ProjectedNode {
  final String id;
  final String label;
  final double x, y, z;
  final double scale;
  final Color color;
  final double activity;
  final bool isSpeaking;

  const _ProjectedNode({
    required this.id,
    required this.label,
    required this.x,
    required this.y,
    required this.z,
    required this.scale,
    required this.color,
    required this.activity,
    required this.isSpeaking,
  });
}
