using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace SyntyrExample.Pages; // Replace with your ASP.NET Core application's namespace.

public sealed class CampaignsModel : PageModel
{
    private static readonly string[] Campaigns =
    [
        "Downtown launch",
        "Airport network",
        "Transit renewal"
    ];

    [BindProperty(SupportsGet = true)]
    public string Query { get; set; } = string.Empty;

    public IReadOnlyList<string> Results { get; private set; } = [];

    public void OnGet()
    {
        string search = (Query ?? string.Empty).Trim();
        Results = Campaigns
            .Where(name => name.Contains(search, StringComparison.OrdinalIgnoreCase))
            .ToArray();
    }
}
