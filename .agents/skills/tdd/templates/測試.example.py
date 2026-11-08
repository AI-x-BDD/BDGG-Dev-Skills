def test_pressing_c_discards_the_pending_operation():
    # Arrange
    calc = Calculator()
    calc.press("5")
    calc.press("+")

    # Act
    calc.press("C")
    calc.press("3")
    calc.press("=")

    # Assert
    assert calc.display == "3"
