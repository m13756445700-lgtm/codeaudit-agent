package lab;
import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class UserService {
 private final UserMapper mapper;
 public UserService(UserMapper mapper) { this.mapper = mapper; }
 public List<Map<String,Object>> raw(String order) {
  return mapper.raw(order);
 }
 public List<Map<String,Object>> bound(String username) {
  return mapper.bound(username);
 }
}
