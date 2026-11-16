# Syntyr in Java and C# server-rendered applications

No Java or .NET Syntyr package is necessary: the portable CSS and the HTML
class/attribute contract are the integration.

## Java / Spring Boot MVC with Thymeleaf

1. Create or use a Spring Boot application with Spring Web and Thymeleaf
   dependencies; use Java 17 or newer.
2. Copy dist/syntyr.core.css into src/main/resources/static/css/.
3. Copy spring-thymeleaf.html to
   src/main/resources/templates/campaigns.html.
4. Copy CampaignSearchController.java into your application's controller
   package; adjust the example.web package declaration.
5. Run the application and open /campaigns?q=airport.

Thymeleaf th:text and th:value escape untrusted values. The example is
read-only GET; for mutating POST routes use Spring Security's CSRF protections
and server-side Bean Validation, with aria-invalid / aria-describedby
on invalid controls. Keep Syntyr's theme root stable across fragment updates.

## C# / ASP.NET Core Razor Pages

1. Create or use an ASP.NET Core Razor Pages project targeting modern .NET
   (the example uses C# collection expressions, available in C# 12+).
2. Copy dist/syntyr.core.css to wwwroot/css/.
3. Copy dotnet/Pages/Campaigns.cshtml and Campaigns.cshtml.cs into Pages/;
   change the SyntyrExample.Pages namespace/@model to your application's.
4. Ensure Razor Pages are enabled/mapped (AddRazorPages and MapRazorPages).
5. Run the app, open /campaigns?Query=airport.

Razor's @Model and @campaign output are encoded by default; do not use
Html.Raw on untrusted values. asp-append-version requires MVC Tag Helpers,
which are explicitly enabled in the sample. The GET query is read-only.
For mutations use the platform's antiforgery, authorization, model validation,
and redirect-after-POST conventions.

Neither template requires JavaScript, an npm install, or a Syntyr JVM/NuGet
adapter. The checked-in Java and C# examples are copy-owned source snippets,
not a complete Spring Boot or ASP.NET project, and require tests in the host
application; the repository's CI only checks their static integration contract.
