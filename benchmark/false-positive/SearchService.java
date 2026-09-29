class SearchService {
    private final UserMapper mapper;
    SearchService(UserMapper mapper) { this.mapper = mapper; }
    Object users(String sort) {
        String column;
        switch (sort) {
            case "name": column = "name"; break;
            case "created": column = "created_at"; break;
            default: column = "id";
        }
        return mapper.users(column);
    }
}
