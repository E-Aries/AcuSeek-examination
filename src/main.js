import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import App from "./App.vue";
import router from "./router";
import "./styles/variables.css"
import favicon from "./images/Favicon.png";

const app = createApp(App);

// Register all Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.use(ElementPlus, { size: "default" });
app.use(router);
// Set favicon from imported image
const faviconLink = document.querySelector("link[rel*='icon']") || document.createElement("link");
faviconLink.rel = "icon";
faviconLink.href = favicon;
document.head.appendChild(faviconLink);

app.mount("#app");
