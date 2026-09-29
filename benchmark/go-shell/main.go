package main
import ("net/http"; "os/exec")
func main() {
 http.HandleFunc("/echo", func(w http.ResponseWriter, r *http.Request) {
  name := r.URL.Query().Get("name")
  out, _ := exec.Command("/bin/sh", "-c", "echo " + name).Output()
  w.Write(out)
 })
 http.ListenAndServe(":8080", nil)
}
