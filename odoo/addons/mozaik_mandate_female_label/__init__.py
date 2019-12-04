from . import models


def _copy_name_to_female_name(cr):
    """
    Create here the female_name and copy name on it
    because it is required in the model
    """
    q = """
    ALTER TABLE mandate_category
    ADD COLUMN IF NOT EXISTS female_name VARCHAR
    """
    cr.execute(q)
    q = """
    UPDATE mandate_category
    SET female_name = name
    WHERE female_name IS NULL
    """
    cr.execute(q)
