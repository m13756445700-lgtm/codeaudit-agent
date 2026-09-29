package main
import ("net/http"; "io")
func main() {
 http.HandleFunc("/fetch", func(w http.ResponseWriter, r *http.Request) {
  target := "https://example.org/a"
  if r.URL.Query().Get("kind") == "b" { target = "https://example.org/b" }
  client := &http.Client{CheckRedirect: func(req *http.Request, via []*http.Request) error { return http.ErrUseLastResponse }}
  resp, err := client.Get(target)
  if err != nil { http.Error(w, "failed", 502); return }
  defer resp.Body.Close()
  io.Copy(w, resp.Body)
 })
 http.ListenAndServe(":8080", nil)
}
