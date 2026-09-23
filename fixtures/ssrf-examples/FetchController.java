package lab;
import java.util.Map;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
@RestController
public class FetchController {
    private final RestTemplate client = new RestTemplate();
    private static final Map<String, String> SERVICES = Map.of("catalog", "https://catalog.example.invalid/items", "status", "https://status.example.invalid/health");
    @GetMapping("/fetch")
    public String raw(@RequestParam String url) {
        return client.getForObject(url, String.class);
    }
    @GetMapping("/service")
    public String mapped(@RequestParam String serviceId) {
        String url = SERVICES.get(serviceId);
        return client.getForObject(url, String.class);
    }
    @GetMapping("/prefix")
    public String prefix(@RequestParam String url) {
        if (!url.startsWith("https://trusted.example.invalid")) throw new IllegalArgumentException();
        return client.getForObject(url, String.class);
    }
}
