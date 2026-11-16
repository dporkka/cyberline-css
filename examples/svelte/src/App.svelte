<script>
  let campaignName = $state('');
  let campaigns = $state(['Downtown launch', 'Airport network']);
  let error = $state('');
  let notice = $state('');
  let saving = $state(false);

  async function addCampaign(event) {
    event.preventDefault();
    if (saving) return;
    const name = campaignName.trim();
    if (!name) {
      error = 'Enter a campaign name.';
      notice = '';
      return;
    }

    saving = true;
    error = '';
    notice = '';
    // Demo-only simulated latency. Replace with your application's real API call.
    await new Promise((resolve) => setTimeout(resolve, 250));
    campaigns = [...campaigns, name];
    campaignName = '';
    saving = false;
    notice = 'Campaign added locally (demo only).';
  }
</script>

<main class="syn-root syn-page" data-syn-theme="studio">
  <section class="syn-panel" aria-labelledby="campaign-heading">
    <h1 id="campaign-heading" class="syn-heading">Campaigns</h1>
    <p>Svelte owns application state; Syntyr provides CSS only.</p>
    <form class="syn-form" onsubmit={addCampaign} aria-busy={saving ? 'true' : 'false'}>
      <div class="syn-field">
        <label class="syn-label" for="campaign-name">Campaign name</label>
        <input
          id="campaign-name"
          bind:value={campaignName}
          class="syn-input"
          name="campaign"
          type="text"
          autocomplete="off"
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? 'campaign-name-error' : undefined}
          oninput={() => (error = '')}
        />
        {#if error}
          <p id="campaign-name-error" class="syn-error">{error}</p>
        {/if}
      </div>
      <button class="syn-button syn-button--primary" type="submit" disabled={saving} data-syn-state={saving ? 'loading' : undefined}>
        {saving ? 'Adding…' : 'Add campaign'}
      </button>
    </form>
    <p role="status" aria-live="polite">{notice}</p>
    <ul aria-label="Campaign list">
      {#each campaigns as campaign, index (index)}
        <li>{campaign}</li>
      {/each}
    </ul>
  </section>
</main>
