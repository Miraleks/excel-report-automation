from generate_sample_data import HEADER, generate_rows, write_csv


def test_generate_rows_count_and_duplicates():
    rows = generate_rows()
    assert len(rows) == 310
    assert len({r[0] for r in rows}) == 300


def test_generate_rows_is_deterministic():
    assert generate_rows(seed=1) == generate_rows(seed=1)


def test_write_csv_creates_folder_and_file(tmp_path):
    out = tmp_path / "data" / "sample_orders.csv"
    write_csv(out, generate_rows())

    assert out.exists()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ";".join(HEADER)
    assert len(lines) == 311