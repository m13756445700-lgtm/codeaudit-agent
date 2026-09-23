import java.nio.file.*;
class PathBoundaryProbe {
    public static void main(String[] args) throws Exception {
        Path root = Files.createTempDirectory("path-boundary-");
        Path base = Files.createDirectory(root.resolve("allowed")).toRealPath();
        Path outside = Files.createDirectory(root.resolve("outside"));
        Files.writeString(outside.resolve("marker"), "CONTROLLED");
        Files.createSymbolicLink(base.resolve("link"), outside);
        Path lexical = base.resolve("link/marker").normalize();
        Path real = lexical.toRealPath();
        boolean lexicalPass = lexical.startsWith(base);
        boolean realPass = real.startsWith(base);
        System.out.println("normalize_boundary_pass=" + lexicalPass);
        System.out.println("realpath_boundary_pass=" + realPass);
        System.out.println("outside_marker_read=" + Files.readString(lexical).equals("CONTROLLED"));
        if (!lexicalPass || realPass) throw new Exception("Unexpected semantics");
    }
}
