import org.springframework.web.bind.annotation.*;

@RestController
class SearchController {
    private final SearchService service;
    SearchController(SearchService service) { this.service = service; }
    @GetMapping("/users")
    Object users(@RequestParam String sort) {
        return service.users(sort);
    }
}
