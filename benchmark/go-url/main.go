package main
import ("net/http"; "io")
func main() {
 http.HandleFunc("/fetch", func(w http.ResponseWriter, r *http.Request) {
  target := r.URL.Query().Get("url")
  resp, err := http.Get(target)
  if err != nil { http.Error(w, "failed", 502); return }
  defer resp.Body.Close()
  io.Copy(w, resp.Body)
 })
 http.ListenAndServe(":8080", nil)
}
