<script setup>
import { ref } from 'vue';

const campaignName = ref('');
const campaigns = ref(['Downtown launch', 'Airport network']);
const error = ref('');
const notice = ref('');
const saving = ref(false);

async function addCampaign() {
  if (saving.value) return;
  const name = campaignName.value.trim();
  if (!name) {
    error.value = 'Enter a campaign name.';
    notice.value = '';
    return;
  }

  saving.value = true;
  error.value = '';
  notice.value = '';
  // Demo-only simulated latency. Replace with your application's real API call.
  await new Promise((resolve) => setTimeout(resolve, 250));
  campaigns.value.push(name);
  campaignName.value = '';
  saving.value = false;
  notice.value = 'Campaign added locally (demo only).';
}
</script>

<template>
  <main class="syn-root syn-page" data-syn-theme="studio">
    <section class="syn-panel" aria-labelledby="campaign-heading">
      <h1 id="campaign-heading" class="syn-heading">Campaigns</h1>
      <p>Vue owns application state; Syntyr provides CSS only.</p>
      <form class="syn-form" @submit.prevent="addCampaign" :aria-busy="saving ? 'true' : 'false'">
        <div class="syn-field">
          <label class="syn-label" for="campaign-name">Campaign name</label>
          <input
            id="campaign-name"
            v-model="campaignName"
            class="syn-input"
            name="campaign"
            type="text"
            autocomplete="off"
            :aria-invalid="error ? 'true' : 'false'"
            :aria-describedby="error ? 'campaign-name-error' : undefined"
            @input="error = ''"
          />
          <p v-if="error" id="campaign-name-error" class="syn-error">{{ error }}</p>
        </div>
        <button class="syn-button syn-button--primary" type="submit" :disabled="saving" :data-syn-state="saving ? 'loading' : undefined">
          {{ saving ? 'Adding…' : 'Add campaign' }}
        </button>
      </form>
      <p role="status" aria-live="polite">{{ notice }}</p>
      <ul aria-label="Campaign list">
        <li v-for="(campaign, index) in campaigns" :key="index">{{ campaign }}</li>
      </ul>
    </section>
  </main>
</template>
