import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'services/api_client.dart';
import 'services/dialogue_state.dart';
import 'screens/home_screen.dart';
import 'theme/psai_theme.dart';

void main() {
  final apiClient = ApiClient();

  runApp(
    MultiProvider(
      providers: [
        Provider<ApiClient>.value(value: apiClient),
        ChangeNotifierProvider(create: (_) => DialogueState(apiClient)),
      ],
      child: const PSAIApp(),
    ),
  );
}

class PSAIApp extends StatelessWidget {
  const PSAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'P.S.AI',
      theme: PSAITheme.dark,
      debugShowCheckedModeBanner: false,
      home: const HomeScreen(),
    );
  }
}
