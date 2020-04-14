from tdg.v1.filler.default import IncrString


def test_incr_string():
    filler = IncrString(prefix='test-', zero_fill=3, suffix='-end', base=0, step=10)

    assert filler.next() == 'test-000-end'
    assert filler.next() == 'test-010-end'
