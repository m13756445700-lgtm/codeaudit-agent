import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

// Isolated semantic check. Only printf writes to a disposable /tmp marker.
class CommandArgvProbe {
    static void run(Process p) throws Exception {
        if (!p.waitFor(5, TimeUnit.SECONDS)) { p.destroyForcibly(); throw new Exception("timeout"); }
    }
    public static void main(String[] args) throws Exception {
        Path marker = Path.of("/tmp/codeaudit-probe-marker");
        Files.deleteIfExists(marker);
        String input = ";printf PROBE>" + marker;
        String command = "sh -c printf " + input;
        String[] tokens = Collections.list(new StringTokenizer(command)).stream().map(Object::toString).toArray(String[]::new);
        System.out.println("single_string_argv=" + Arrays.toString(tokens));
        run(Runtime.getRuntime().exec(command));
        boolean single = Files.exists(marker);
        run(Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", "printf %s " + input}));
        boolean explicit = Files.exists(marker) && Files.readString(marker).equals("PROBE");
        Files.deleteIfExists(marker);
        System.out.println("single_string_marker=" + single);
        System.out.println("explicit_argv_marker=" + explicit);
        if (single || !explicit) throw new Exception("unexpected semantics");
    }
}
