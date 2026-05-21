from deps_ai_fusion import constants


class TestHealthcheck:
    endpoint = constants.BASE_API_PREFIX

    def test_healthcheck_endpoint_return_200(self, client, postgres_datasource_mock):
        postgres_datasource_mock.healthcheck.return_value = ""
        response = client.get(f"{self.endpoint}/healthcheck")

        assert response.status_code == 200

    def test_healthcheck_endpoint_return_503(self, client, postgres_datasource_mock):
        postgres_datasource_mock.healthcheck.side_effect = Exception("Service unavailable")
        response = client.get(f"{self.endpoint}/healthcheck")

        assert response.status_code == 503
