from payment import charge_payment


def test_charge_payment_prints_charge_message(capsys) -> None:
    charge_payment("40", 500)

    output = capsys.readouterr().out

    assert "Charging user 40 amount 500 using stripe" in output
