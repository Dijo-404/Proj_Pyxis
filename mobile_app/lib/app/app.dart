import 'package:flutter/material.dart';
import 'package:pyxis_mobile/app/router.dart';
import 'package:pyxis_mobile/app/theme.dart';

class PyxisApp extends StatelessWidget {
  const PyxisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pyxis',
      debugShowCheckedModeBanner: false,
      theme: buildPyxisTheme(),
      initialRoute: AppRoutes.commandCenter,
      routes: {
        AppRoutes.commandCenter: (_) => const _ScaffoldPlaceholder(),
      },
    );
  }
}

class _ScaffoldPlaceholder extends StatelessWidget {
  const _ScaffoldPlaceholder();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Text('Pyxis Compliance Command Center'),
      ),
    );
  }
}
