package lab;
import org.springframework.web.bind.annotation.*;
import java.util.*;
@RestController
public class UserController {
 private final UserService service;
 public UserController(UserService service) { this.service = service; }
 @GetMapping("/users/raw")
 public List<Map<String,Object>> raw(@RequestParam String order) {
  return service.raw(order);
 }
 @GetMapping("/users/bound")
 public List<Map<String,Object>> bound(@RequestParam String username) {
  return service.bound(username);
 }
}
