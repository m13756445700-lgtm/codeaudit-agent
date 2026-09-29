import org.springframework.web.bind.annotation.*;
@RestController
class EchoController {
 @GetMapping("/echo")
 String echo(@RequestParam String name) throws Exception {
  Runtime.getRuntime().exec("/bin/echo " + name);
  return "ok";
 }
}
