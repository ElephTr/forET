---
name: ai-nav-site
description: Deploy an AI navigation website using Tomcat. Creates a categorized directory of AI tools (LLMs, image/video generation, coding assistants, etc.) with search functionality. Use when the user wants to build and host an AI tools navigation/directory website on a Tomcat server with external access.
---

# AI Navigation Site Skill

Deploy a beautiful, searchable AI tools navigation website using Apache Tomcat.

## What This Skill Creates

A responsive web page that categorizes and links to major AI tools:
- Large Language Models (ChatGPT, Claude, Gemini, Kimi, etc.)
- AI Image Generation (Midjourney, DALL-E, Stable Diffusion)
- AI Video Generation (Sora, Runway, 可灵 AI)
- AI Coding Assistants (Copilot, Cursor, Codeium)
- AI Audio/Music (ElevenLabs, Suno)
- AI Search Engines (Perplexity, You.com)

## Quick Deploy

### Prerequisites

- Linux server with internet access
- Root or sudo access
- Port 8080 available (or configure a different port)

### Deploy Steps

1. **Install Java (JDK)**
   ```bash
   apt-get update && apt-get install -y default-jdk
   ```

2. **Download and Extract Tomcat**
   ```bash
   cd /opt
   wget https://archive.apache.org/dist/tomcat/tomcat-10/v10.1.34/bin/apache-tomcat-10.1.34.tar.gz
   tar -xzf apache-tomcat-10.1.34.tar.gz
   ```

3. **Create the Website**
   - Copy `assets/index.html` to `/opt/apache-tomcat-10.1.34/webapps/ai-nav/index.html`

4. **Configure External Access**
   - Edit `/opt/apache-tomcat-10.1.34/conf/server.xml`
   - Find the Connector port="8080" element
   - Add `address="0.0.0.0"` attribute

5. **Start Tomcat**
   ```bash
   export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
   /opt/apache-tomcat-10.1.34/bin/startup.sh
   ```

6. **Access the Site**
   - Local: http://localhost:8080/ai-nav/
   - External: http://YOUR_SERVER_IP:8080/ai-nav/

## Customization

### Adding New AI Tools

Edit `webapps/ai-nav/index.html` and add new cards:

```html
<a href="https://example.com" class="site-card" target="_blank">
    <div class="site-name">Tool Name</div>
    <div class="site-desc">Brief description</div>
    <div class="site-url">example.com</div>
    <span class="tag">免费/付费</span>
</a>
```

### Changing Port

Edit `conf/server.xml`:
```xml
<Connector port="YOUR_PORT" protocol="HTTP/1.1" ... />
```

### Stopping Tomcat

```bash
/opt/apache-tomcat-10.1.34/bin/shutdown.sh
```

## File Structure

```
apache-tomcat-10.1.34/
├── bin/           # Startup/shutdown scripts
├── conf/          # Configuration files
├── webapps/
│   └── ai-nav/
│       └── index.html   # The navigation website
└── logs/          # Server logs
```

## Troubleshooting

- **Port already in use**: Change the port in `conf/server.xml`
- **Cannot access externally**: Check firewall rules and `address="0.0.0.0"` in server.xml
- **Java not found**: Install JDK and set JAVA_HOME environment variable
