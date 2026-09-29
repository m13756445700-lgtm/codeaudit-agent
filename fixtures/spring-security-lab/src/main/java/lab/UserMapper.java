package lab;
import org.apache.ibatis.annotations.*;
import java.util.*;
@Mapper
public interface UserMapper {
 List<Map<String,Object>> raw(@Param("order") String order);
 List<Map<String,Object>> bound(@Param("username") String username);
}
