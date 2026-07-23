import XCTest
@testable import Pyxis

final class ThemeTests: XCTestCase {
    func testRiskBandThresholds() {
        XCTAssertEqual(riskBand(85).label, "Critical")
        XCTAssertEqual(riskBand(80).label, "Critical")
        XCTAssertEqual(riskBand(79).label, "High")
        XCTAssertEqual(riskBand(60).label, "High")
        XCTAssertEqual(riskBand(59).label, "Medium")
        XCTAssertEqual(riskBand(35).label, "Medium")
        XCTAssertEqual(riskBand(34).label, "Low")
        XCTAssertEqual(riskBand(0).label, "Low")
    }
}
