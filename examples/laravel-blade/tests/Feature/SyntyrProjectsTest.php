<?php

namespace Tests\Feature;

use Tests\TestCase;

class SyntyrProjectsTest extends TestCase
{
    public function test_search_filters_project_rows(): void
    {
        $response = $this->get('/syntyr/projects?q=airport');
        $response->assertOk()
            ->assertSee('Airport displays')
            ->assertDontSee('Station expansion');
    }

    public function test_search_escapes_user_input(): void
    {
        $response = $this->get('/syntyr/projects?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E');
        $response->assertOk()
            ->assertSee('&lt;script&gt;alert(1)&lt;/script&gt;', false)
            ->assertDontSee('<script>alert(1)</script>', false);
    }
}
