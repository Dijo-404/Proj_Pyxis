import 'package:flutter_test/flutter_test.dart';
import 'package:pyxis_mobile/app/app.dart';

void main() {
  testWidgets('shows the command center placeholder', (tester) async {
    await tester.pumpWidget(const PyxisApp());

    expect(find.text('Pyxis Compliance Command Center'), findsOneWidget);
  });
}
