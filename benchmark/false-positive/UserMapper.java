import org.apache.ibatis.annotations.Param;
interface UserMapper {
    Object users(@Param("column") String column);
}
