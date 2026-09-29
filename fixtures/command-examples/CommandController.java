package lab;
import java.util.Map;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
@RestController
public class CommandController {
    private static final Map<String, String> HOST_MAP = Map.of("local", "127.0.0.1", "backup", "192.0.2.1");
    @GetMapping("/command")
    public void unsafe(@RequestParam String host) throws Exception {
        String cmd = "printf %s " + host;
        Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", cmd});
    }
    @GetMapping("/legacy")
    public void legacy(@RequestParam String host) throws Exception {
        String cmd = "sh -c ping " + host;
        Runtime.getRuntime().exec(cmd);
    }
    @GetMapping("/mapped")
    public void safe(@RequestParam String input) throws Exception {
        String mapped = HOST_MAP.get(input);
        new ProcessBuilder("/usr/bin/ping", "-c", "1", mapped).start();
    }
}
