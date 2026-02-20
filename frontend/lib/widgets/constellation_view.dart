import 'dart:math';
import 'package:flutter/material.dart';
import 'constellation_painter.dart';

/// Interactive 3D constellation view with ambient rotation,
/// momentum-based pan, and persona node rendering.
class ConstellationView extends StatefulWidget {
  final List<ConstellationNode> nodes;
  final String? activeSpeakerId;

  const ConstellationView({
    super.key,
    required this.nodes,
    this.activeSpeakerId,
  });

  @override
  State<ConstellationView> createState() => _ConstellationViewState();
}

class _ConstellationViewState extends State<ConstellationView>
    with TickerProviderStateMixin {
  late AnimationController _rotationController;
  late AnimationController _pulseController;

  double _rotationX = 0.0;
  double _rotationY = 0.0;

  // Momentum-based pan
  double _velocityX = 0.0;
  double _velocityY = 0.0;
  static const double _friction = 0.95;
  static const double _ambientSpeed = 0.001; // radians per frame

  @override
  void initState() {
    super.initState();

    // Ambient rotation (60s full revolution)
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 60),
    )..repeat();
    _rotationController.addListener(_onRotationTick);

    // Speaking pulse (2s period)
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
  }

  void _onRotationTick() {
    setState(() {
      // Apply ambient rotation
      _rotationY += _ambientSpeed;

      // Apply momentum
      _rotationX += _velocityX;
      _rotationY += _velocityY;
      _velocityX *= _friction;
      _velocityY *= _friction;

      // Dampen small velocities
      if (_velocityX.abs() < 0.0001) _velocityX = 0;
      if (_velocityY.abs() < 0.0001) _velocityY = 0;
    });
  }

  @override
  void dispose() {
    _rotationController.removeListener(_onRotationTick);
    _rotationController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: (details) {
        setState(() {
          _velocityY += details.delta.dx * 0.003;
          _velocityX -= details.delta.dy * 0.003;
        });
      },
      child: AnimatedBuilder(
        animation: _pulseController,
        builder: (context, _) {
          return CustomPaint(
            painter: ConstellationPainter(
              nodes: widget.nodes,
              rotationX: _rotationX,
              rotationY: _rotationY,
              activeSpeakerId: widget.activeSpeakerId,
              pulsePhase: _pulseController.value,
            ),
            size: Size.infinite,
          );
        },
      ),
    );
  }
}
