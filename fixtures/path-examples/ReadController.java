package lab;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
@RestController
public class ReadController {
    private static final String BASE_DIR = "/srv/allowed";
    @GetMapping("/read")
    public String raw(@RequestParam String filename) throws Exception {
        String path = BASE_DIR + "/" + filename;
        return Files.readString(Paths.get(path));
    }
    @GetMapping("/normalized")
    public String normalized(@RequestParam String filename) throws Exception {
        Path base = Paths.get(BASE_DIR).toRealPath();
        Path target = base.resolve(filename).normalize();
        if (!target.startsWith(base)) { throw new SecurityException(); }
        return Files.readString(target);
    }
    @GetMapping("/real")
    public String canonical(@RequestParam String filename) throws Exception {
        Path base = Paths.get(BASE_DIR).toRealPath();
        Path target = base.resolve(filename).toRealPath();
        if (!target.startsWith(base)) { throw new SecurityException(); }
        return Files.readString(target);
    }
}
