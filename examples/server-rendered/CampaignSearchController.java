package example.web; // Replace with your Spring Boot application's package.

import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

/** Read-only demonstration using Spring MVC + Thymeleaf; no database or Syntyr Java dependency. */
@Controller
public class CampaignSearchController {
    private static final List<String> CAMPAIGNS = List.of(
        "Downtown launch", "Airport network", "Transit renewal");

    @GetMapping("/campaigns")
    public String campaigns(@RequestParam(name = "q", defaultValue = "") String query, Model model) {
        String search = query.strip().toLowerCase(Locale.ROOT);
        List<String> results = CAMPAIGNS.stream()
            .filter(name -> name.toLowerCase(Locale.ROOT).contains(search))
            .toList();
        model.addAttribute("query", query);
        model.addAttribute("campaigns", results);
        return "campaigns";
    }
}
