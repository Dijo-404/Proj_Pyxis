/// Transport boundary for the local Pyxis REST API.
///
/// Authentication and Dio configuration are added with the first authenticated
/// feature so token handling is designed together with the backend contract.
final class ApiClient {
  ApiClient({required this.baseUri});

  final Uri baseUri;
}
