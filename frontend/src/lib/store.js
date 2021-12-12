import { writable } from "svelte/store";
import { derived } from "svelte/store";

export const user = writable("");

export const branch_filter = writable("");
export const show_only_running = writable("");

export function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

// This can only be run in the browser not during
// SSR time so we delay it till onMount in the main
// app
export const initStores = () => {
  branch_filter.set(localStorage.getItem("filter") || "");
  branch_filter.subscribe((value) => {
    localStorage.setItem("filter", value);
  });
  show_only_running.set(
    localStorage.getItem("show_only_running") == "false" ? false : true
  );
  show_only_running.subscribe((value) => {
    localStorage.setItem("show_only_running", value);
  });
  user.set(readCookie("username"));
};
