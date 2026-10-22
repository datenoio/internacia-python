"""Tests to verify no numpy.ndarray types are returned from any function."""

from internacia.countries import CountriesClient
from internacia.intblocks import IntblocksClient


def _check_no_numpy(obj, path=""):
    """
    Recursively check that no numpy.ndarray types are present in the object.

    Args:
        obj: Object to check
        path: Current path in the object structure (for error messages)

    Returns:
        List of paths where numpy arrays were found (empty if none found)
    """
    issues = []

    # Check if object is a numpy array
    try:
        import numpy as np

        if isinstance(obj, np.ndarray):
            issues.append(f"{path}: numpy.ndarray found")
            return issues
    except ImportError:
        # numpy not installed, skip check
        pass

    # Recursively check collections
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            issues.extend(_check_no_numpy(value, new_path))
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            issues.extend(_check_no_numpy(item, new_path))

    return issues


class TestNoNumpyInCountries:
    """Test that CountriesClient methods never return numpy arrays."""

    def test_get_by_code_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_code returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_code("US")

        if result is not None:
            issues = _check_no_numpy(result)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_iso3_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_iso3 returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_iso3("USA")

        if result is not None:
            issues = _check_no_numpy(result)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_numeric_code_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_numeric_code returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_numeric_code("840")

        if result is not None:
            issues = _check_no_numpy(result)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_all_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_all returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_all()

        assert isinstance(result, list)
        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_region_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_region returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_region("NAC")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_income_level_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_income_level returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_income_level("HIC")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_un_members_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_un_members returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_un_members()

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_independent_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_independent returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_independent()

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_continent_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_continent returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_continent("North America")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_currency_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_currency returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_currency("USD")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_language_no_numpy(self, mock_db_manager, sample_country_data):
        """Test get_by_language returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_country_data]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_language("eng")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_count_no_numpy(self, mock_db_manager):
        """Test count returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [{"count": 195}]
        client = CountriesClient(mock_db_manager)

        result = client.count()

        # count() returns an int, not a dict/list
        assert isinstance(result, int)
        assert not isinstance(result, (list, dict))


class TestNoNumpyInIntblocks:
    """Test that IntblocksClient methods never return numpy arrays."""

    def test_get_by_id_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_id returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_id("EU")

        if result is not None:
            issues = _check_no_numpy(result)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_all_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_all returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_all()

        assert isinstance(result, list)
        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_blocktype_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_blocktype returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_blocktype("economic")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_status_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_status returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_status("formal")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_geographic_scope_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_geographic_scope returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_geographic_scope("regional")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_member_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_member returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_member("US")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_acronym_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_acronym returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_acronym("EU")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_tag_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_tag returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_tag("trade")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_topic_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_topic returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_topic("economy")

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_get_by_founded_year_no_numpy(self, mock_db_manager, sample_block_data):
        """Test get_by_founded_year returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [sample_block_data]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_founded_year(1993)

        for item in result:
            issues = _check_no_numpy(item)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_count_no_numpy(self, mock_db_manager):
        """Test count returns no numpy arrays."""
        mock_db_manager.execute_query_dict.return_value = [{"count": 50}]
        client = IntblocksClient(mock_db_manager)

        result = client.count()

        # count() returns an int, not a dict/list
        assert isinstance(result, int)
        assert not isinstance(result, (list, dict))


class TestNoNumpyInComplexData:
    """Test that complex nested data structures contain no numpy arrays."""

    def test_country_with_nested_data_no_numpy(self, mock_db_manager):
        """Test country with nested structures contains no numpy arrays."""
        complex_country = {
            "code": "US",
            "name": "United States",
            "capital_city": {"name": "Washington", "lng": -77.0, "lat": 38.9},
            "region": {"id": "NAC", "value": "North America"},
            "incomeLevel": {"id": "HIC", "value": "High income"},
            "languages": [{"code": "eng", "name": "English", "official": True}],
            "currencies": [{"code": "USD", "name": "United States dollar", "symbol": "$"}],
            "continents": ["North America"],
            "borders": ["CA", "MX"],
            "native_names": {
                "eng": {"common": "United States", "official": "United States of America"}
            },
            "un_member": True,
            "independent": True,
        }
        mock_db_manager.execute_query_dict.return_value = [complex_country]
        client = CountriesClient(mock_db_manager)

        result = client.get_by_code("US")

        if result is not None:
            issues = _check_no_numpy(result)
            assert not issues, f"Found numpy arrays: {issues}"

    def test_intblock_with_nested_data_no_numpy(self, mock_db_manager):
        """Test intblock with nested structures contains no numpy arrays."""
        complex_block = {
            "id": "EU",
            "name": "European Union",
            "blocktype": ["economic", "political"],
            "status": "formal",
            "translations": [
                {"lang": "en", "name": "European Union"},
                {"lang": "ru", "name": "Европейский союз"},
            ],
            "acronyms": [{"lang": "en", "value": "EU"}, {"lang": "fr", "value": "UE"}],
            "includes": [{"id": "DE", "name": "Germany", "type": "member", "status": "active"}],
            "tags": ["trade", "economic", "political"],
            "topics": [{"key": "economy", "name": "Economy"}, {"key": "trade", "name": "Trade"}],
            "founded": "1993-11-01",
            "geographic_scope": "regional",
        }
        mock_db_manager.execute_query_dict.return_value = [complex_block]
        client = IntblocksClient(mock_db_manager)

        result = client.get_by_id("EU")

        if result is not None:
            issues = _check_no_numpy(result)
            assert not issues, f"Found numpy arrays: {issues}"
