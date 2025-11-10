<template>
  <div class="outter-header">
    因應災區需求減少，媒合功能將於
    <span style="color: #ef5756">10/30</span> 關閉，<br />
    若有物資需求，請至
    <a href="https://gf250923.org/map" target="_parent" style="color: #36c1ef"
      >地圖頁</a
    >
    導航物資站
  </div>
  <div class="app-shell">
    <header class="page-header">
      <div class="header-main">
        <div class="header-left">
          <h1>我要配送</h1>
        </div>
        <div class="header-right">
          <el-button
            class="create-btn"
            type="primary"
            :icon="Plus"
            @click="openCreate"
          >
            新增配送需求
          </el-button>
        </div>
      </div>
      <div class="header-note">
        <div style="padding-left: 12px">
          ⚠ 此表單為蜜蜂配給媒合用，捐物資請寄：
        </div>
        <ul style="margin: 6px 0 0 0">
          <li>糖廠「大倉」- 縣府 0937909124 花蓮縣光復鄉糖廠街18號</li>
        </ul>
      </div>
    </header>

    <main class="page-main">
      <div class="list-controls">
        <el-select
          v-model="selectedTag"
          class="tag-filter"
          clearable
          placeholder="篩選類別"
          size="large"
        >
          <el-option
            v-for="option in tagFilterOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <el-checkbox v-model="showPendingOnly" class="pending-checkbox">
          只顯示待配送項目
        </el-checkbox>
        <el-checkbox v-model="showFulfilledOnly" class="pending-checkbox">
          只顯示已完成配送項目
        </el-checkbox>
      </div>

      <el-skeleton v-if="loading" class="loading" :rows="6" animated />

      <template v-else>
        <div v-if="visibleRequests.length > 0" class="cards-grid">
          <el-card
            v-for="req in visibleRequests"
            :key="req.id"
            class="request-card"
            :class="cardClasses(req)"
            :shadow="isCompleted(req) ? 'never' : 'hover'"
          >
            <div
              class="card-main"
              :class="{ 'is-clickable': isCompleted(req) }"
              @click="handleCardClick(req)"
            >
              <div class="card-header">
                <div class="card-header-top">
                  <div class="card-title">
                    <h2>{{ req.org }}</h2>
                    <div class="tags">
                      <el-tag
                        v-for="tag in cardTags(req)"
                        :key="tag.value"
                        size="small"
                        :style="{ backgroundColor: tag.color }"
                        effect="dark"
                      >
                        {{ tag.label }}
                      </el-tag>
                      <el-tag
                        size="small"
                        :type="requestStatus(req).type"
                        effect="dark"
                      >
                        {{ requestStatus(req).label }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="published-at">
                    <el-icon><Clock /></el-icon>
                    <span class="meta-text"
                      >發布 {{ formatTimeAgo(req.created_at) }}</span
                    >
                  </div>
                </div>
              </div>

              <div v-show="!isCompletedCollapsed(req)" class="card-body">
                <!-- Disable showing supply provider info as no one would write data currently -->

                <!--
                <div v-if="!isCompleted(req)" class="card-stations">
                  <div class="section-title">物資站聯絡</div>
                  <div
                    v-if="stationsForRequest(req).length"
                    class="station-scroll"
                  >
                    <div
                      v-for="station in stationsForRequest(req)"
                      :key="station.id"
                      class="station-card"
                    >
                      <div class="station-header">
                        <span class="station-name">{{ station.name }}</span>
                        <div class="station-note">{{ station.notes }}</div>
                        <el-link
                          v-if="station.address"
                          class="contact-row station-link station-link-address"
                          :href="mapLink(station.address)"
                          target="_blank"
                          :underline="false"
                          @click.stop
                        >
                          <el-icon><Location /></el-icon>
                          <span
                            class="station-link-text station-link-text-address"
                          >
                            {{ station.address }}
                          </span>
                          <el-icon class="contact-link-icon"
                            ><TopRight
                          /></el-icon>
                        </el-link>
                        <el-link
                          v-if="station.phone"
                          class="contact-row station-link station-link-phone"
                          :href="phoneHref(station.phone)"
                          :underline="false"
                          @click.stop
                        >
                          <el-icon><Phone /></el-icon>
                          <span
                            class="station-link-text station-link-text-phone"
                          >
                            {{ station.phone }}
                          </span>
                        </el-link>
                      </div>

                      <div
                        v-if="station.supplies?.length"
                        class="station-supplies"
                      >
                        <div class="station-supplies-title">可支援物資</div>
                        <ul class="station-supplies-list">
                          <li
                            v-for="supply in station.supplies"
                            :key="`${station.id}-${supply.id}`"
                            class="station-supply-row"
                          >
                            <span class="supply-name">{{ supply.name }}</span>
                            <span
                              v-if="
                                supply.count !== null &&
                                supply.count !== undefined
                              "
                              class="supply-count"
                            >
                              {{ supply.count
                              }}<template v-if="supply.unit">{{
                                supply.unit
                              }}</template>
                            </span>
                          </li>
                        </ul>
                      </div>

                      <div v-else class="station-supplies-empty">
                        暫無物資資訊
                      </div>
                    </div>
                  </div>
                  <div v-else class="station-empty">
                    尋寶超人正在連線中，馬上幫你找到物資站！
                  </div>
                </div>
                -->

                <div class="card-contact">
                  <div class="section-title">居民聯絡</div>
                  <div class="contact-info">
                    <el-link
                      class="contact-row contact-link contact-link-map"
                      :href="mapLink(req.address)"
                      target="_blank"
                      :underline="true"
                      @click.stop
                    >
                      <el-icon><Location /></el-icon>
                      <span class="meta-text">{{ req.address }}</span>
                      <el-icon class="contact-link-icon"><TopRight /></el-icon>
                    </el-link>
                    <el-link
                      v-if="displayPhone(req)"
                      class="contact-row contact-link contact-link-phone"
                      :href="phoneHref(displayPhone(req))"
                      :underline="false"
                      @click.stop
                    >
                      <el-icon><Phone /></el-icon>
                      <span class="meta-text">{{ displayPhone(req) }}</span>
                    </el-link>
                  </div>
                </div>

                <div class="card-content">
                  <div class="section-title">需求（人力可填寫志工媒合）</div>
                  <div
                    v-for="{ item, index } in pendingItems(req)"
                    :key="`${req.id}-${index}`"
                    class="item-row"
                    :class="{ 'is-fulfilled': isItemFulfilled(item) }"
                  >
                    <div class="item-info">
                      <div class="item-title">
                        <span class="item-name">{{ item.name }}</span>
                        <el-tag
                          size="small"
                          :style="{
                            backgroundColor: typeMeta(item.type).color,
                          }"
                          effect="dark"
                        >
                          {{ typeMeta(item.type).label }}
                        </el-tag>
                      </div>
                      <div class="item-description">
                        <span>需求 {{ item.need }}{{ item.unit }}</span>
                        <span>
                          已收到 {{ item.got }}/{{ item.need
                          }}{{ item.unit }}，還需要：
                          <strong class="need-number"
                            >{{ remainingNeed(item) }}{{ item.unit }}</strong
                          >
                        </span>
                      </div>
                    </div>
                    <el-progress
                      :percentage="progressPercentage(item)"
                      :status="itemProgressStatus(item)"
                    />
                  </div>

                  <div
                    v-if="
                      pendingItems(req).length === 0 &&
                      fulfilledItems(req).length > 0
                    "
                    class="all-fulfilled-hint"
                  >
                    全部物資已完成，以下為各項紀錄
                  </div>

                  <div
                    v-if="fulfilledItems(req).length > 0"
                    class="fulfilled-items"
                  >
                    <div class="fulfilled-header">
                      <span class="fulfilled-title"
                        >已完成項目（{{ fulfilledItems(req).length }}）</span
                      >
                      <el-button
                        text
                        size="small"
                        class="fulfilled-toggle-btn"
                        @click.stop="toggleFulfilledCollapse(req)"
                      >
                        <span>{{
                          isFulfilledCollapsed(req) ? "展開" : "收合"
                        }}</span>
                        <el-icon
                          :class="[
                            'fulfilled-toggle-icon',
                            { 'is-open': !isFulfilledCollapsed(req) },
                          ]"
                        >
                          <ArrowDown />
                        </el-icon>
                      </el-button>
                    </div>

                    <div
                      v-show="!isFulfilledCollapsed(req)"
                      class="fulfilled-list"
                    >
                      <div
                        v-for="{ item, index } in fulfilledItems(req)"
                        :key="`fulfilled-${req.id}-${index}`"
                        class="item-row is-fulfilled"
                      >
                        <div class="item-info">
                          <div class="item-title">
                            <span class="item-name">{{ item.name }}</span>
                            <el-tag
                              size="small"
                              :style="{
                                backgroundColor: typeMeta(item.type).color,
                              }"
                              effect="dark"
                            >
                              {{ typeMeta(item.type).label }}
                            </el-tag>
                          </div>
                          <div class="item-description">
                            <span>需求 {{ item.need }}{{ item.unit }}</span>
                            <span>
                              已收到 {{ item.got }}/{{ item.need
                              }}{{ item.unit }}，還需要：
                              <strong class="need-number"
                                >{{ remainingNeed(item)
                                }}{{ item.unit }}</strong
                              >
                            </span>
                          </div>
                        </div>
                        <el-progress
                          :percentage="progressPercentage(item)"
                          :status="itemProgressStatus(item)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <template #footer>
              <div
                class="card-footer"
                :class="{ 'is-clickable': isCompleted(req) }"
                @click="isCompleted(req) ? handleCardClick(req) : null"
              >
                <div v-if="!isCompleted(req)" class="card-actions">
                  <el-button
                    type="primary"
                    :icon="Van"
                    @click.stop="openDelivery(req)"
                  >
                    我要配送
                  </el-button>
                </div>
                <div v-if="isCompleted(req)" class="completed-toggle">
                  <el-button
                    :class="[
                      'completed-toggle-btn',
                      { 'is-expanded': !isCompletedCollapsed(req) },
                    ]"
                    circle
                    plain
                    size="small"
                    @click.stop="handleCardClick(req)"
                  >
                    <el-icon>
                      <ArrowDown />
                    </el-icon>
                  </el-button>
                </div>
              </div>
            </template>

            <div v-if="isCompleted(req)" class="card-stamp">已完成</div>
          </el-card>
        </div>

        <div v-else-if="loadingMore || hasMore" class="loading-placeholder">
          <el-skeleton :rows="1" animated />
        </div>

        <el-empty v-else description="目前沒有物資需求" />

        <div
          v-if="supportsIntersectionObserver"
          ref="loadMoreTrigger"
          class="infinite-scroll-trigger"
        />

        <div v-if="loadingMore" class="loading-more">
          <el-skeleton :rows="1" animated />
        </div>

        <div v-else-if="!hasMore && visibleRequests.length > 0" class="no-more">
          已載入全部需求<span v-if="totalItems"
            >（共 {{ totalItems }} 筆）</span
          >
        </div>

        <div
          v-if="!supportsIntersectionObserver && hasMore && !loadingMore"
          class="load-more-fallback"
        >
          <el-button
            type="primary"
            plain
            size="small"
            @click="loadMoreRequests"
          >
            載入更多
          </el-button>
        </div>
      </template>
    </main>

    <footer class="page-footer">
      若您有能力提供物資，請優先以「我要配送」填寫可支援的數量，感謝協助。
    </footer>

    <!-- Create Dialog -->
    <el-dialog
      v-model="createDialogVisible"
      title="需求清單"
      class="dialog-responsive"
      :style="{ maxHeight: '70vh', overflow: 'auto' }"
      @closed="onCreateClosed"
    >
      <el-form label-position="top" class="form-grid">
        <el-form-item label="單位名稱" required>
          <el-input v-model.trim="createForm.org" placeholder="污泥暫置場" />
        </el-form-item>
        <el-form-item label="電話">
          <el-input
            v-model.trim="createForm.phone"
            placeholder="0912345678"
            type="tel"
          />
          <span class="hint with-icon">
            <el-icon><WarningFilled /></el-icon>
            填寫電話可幫助資訊傳遞，將會公開在網路上，取得所需物資後會自動隱藏
          </span>
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input
            v-model.trim="createForm.address"
            placeholder="花蓮縣光復鄉..."
          />
        </el-form-item>
      </el-form>

      <section class="materials-section">
        <div class="materials-header">
          <h3>需求項目<span class="required">*</span></h3>
        </div>

        <span class="hint with-icon" style="margin: 0">
          <el-icon><WarningFilled /></el-icon>
          便當需求請註明時間 -「便當 (10/23午餐)」
        </span>

        <div v-if="createForm.items.length === 0" class="items-empty">
          請新增至少一項物資需求
        </div>

        <div
          v-for="(item, index) in createForm.items"
          :key="`create-${index}`"
          class="material-row"
        >
          <el-select
            v-model="item.type"
            placeholder="選擇類型"
            class="material-type-select"
          >
            <el-option
              v-for="option in typeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-input v-model.trim="item.name" placeholder="物資（瓶裝水）" />
          <el-input-number
            v-model="item.need"
            :min="1"
            :max="999999"
            class="material-need-input"
          />
          <el-input
            v-model.trim="item.unit"
            placeholder="單位（箱）"
            class="material-unit-input"
          />
          <el-button
            v-if="createForm.items.length > 1"
            type="danger"
            link
            @click="removeCreateItem(index)"
          >
            移除
          </el-button>
        </div>

        <el-button
          type="primary"
          class="add-item-button"
          :icon="Plus"
          @click="addCreateItem"
        >
          新增需求
        </el-button>
      </section>

      <el-checkbox v-model="createPolicyAccepted" class="policy-checkbox">
        <span class="required-icon">*</span>我已理解本平台
        <el-link
          href="https://gf250923.org/terms"
          target="_blank"
          type="primary"
          :underline="false"
        >
          服務條款
        </el-link>
        及
        <el-link
          href="https://gf250923.org/privacy"
          target="_blank"
          type="primary"
          :underline="false"
        >
          隱私權政策
        </el-link>
        之使用
      </el-checkbox>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!isCreateValid || submitting.create"
          @click="openCreateConfirm"
        >
          確認新增
        </el-button>
      </template>
    </el-dialog>

    <!-- Create Confirm -->
    <el-dialog
      v-model="createConfirmVisible"
      title="確認新增"
      class="dialog-responsive dialog-confirm"
      :style="{ maxHeight: '70vh', overflow: 'auto' }"
    >
      <el-descriptions border :column="1" size="small">
        <el-descriptions-item label="單位名稱">
          {{ createPayload.org }}
        </el-descriptions-item>
        <el-descriptions-item label="地址">
          {{ createPayload.address }}
        </el-descriptions-item>
        <el-descriptions-item label="電話">
          {{ createPayload.phone }}
        </el-descriptions-item>
      </el-descriptions>

      <el-table
        v-if="createSummaryItems.length > 0"
        :data="createSummaryItems"
        border
        size="small"
        style="margin-top: 16px"
      >
        <el-table-column prop="name" label="物資" />
        <el-table-column label="類型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.typeLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="need" label="需求數量" width="120">
          <template #default="{ row }"> {{ row.need }}{{ row.unit }} </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="createConfirmVisible = false">返回修改</el-button>
        <el-button
          type="primary"
          :loading="submitting.create"
          @click="submitCreate"
        >
          送出
        </el-button>
      </template>
    </el-dialog>

    <!-- Delivery Dialog -->
    <el-dialog
      v-model="deliveryDialogVisible"
      title="配送清單"
      class="dialog-responsive delivery-dialog"
      @closed="onDeliveryClosed"
    >
      <p class="hint">目前配送進度</p>

      <el-empty
        v-if="deliveryDisplayItems.length === 0"
        description="此需求已完成"
      />

      <div v-else class="delivery-list">
        <div
          v-for="item in deliveryDisplayItems"
          :key="`deliver-${item.index}`"
          class="deliver-card"
        >
          <div class="deliver-header">
            <div class="deliver-title">
              <strong>{{ item.name }}</strong>
              <el-tag size="small">{{ typeMeta(item.type).label }}</el-tag>
            </div>
            <span class="muted"
              >尚缺 {{ remainingNeed(item) }}{{ item.unit }}</span
            >
          </div>
          <el-progress
            :percentage="progressPercentage(item)"
            :status="itemProgressStatus(item)"
            :text-inside="true"
            stroke-width="18"
          />
          <div class="deliver-actions">
            <el-input-number
              class="deliver-input"
              :model-value="deliveryPicks[item.index] ?? 0"
              :min="0"
              :max="remainingNeed(item)"
              @update:model-value="(val) => setDeliveryPick(item.index, val)"
            />
            <el-button
              size="small"
              @click="setDeliveryPick(item.index, remainingNeed(item))"
            >
              MAX
            </el-button>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="delivery-footer">
          <el-button
            type="primary"
            text
            @click="openDeliverAllConfirm"
            :disabled="deliveryDisplayItems.length === 0"
          >
            全部送達
          </el-button>
          <div class="footer-actions">
            <el-button @click="deliveryDialogVisible = false">取消</el-button>
            <el-button
              type="primary"
              :disabled="!canConfirmDelivery || submitting.delivery"
              @click="openDeliveryConfirm"
            >
              確認配送
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- Delivery Confirm -->
    <el-dialog
      v-model="deliveryConfirmVisible"
      title="確認配送"
      class="dialog-responsive dialog-confirm"
    >
      <el-descriptions v-if="deliveryTarget" border :column="1" size="small">
        <el-descriptions-item label="配送到">
          {{ deliveryTarget.org }}
        </el-descriptions-item>
        <el-descriptions-item label="地址">
          {{ deliveryTarget.address }}
        </el-descriptions-item>
      </el-descriptions>

      <el-table
        v-if="deliverySummaryItems.length > 0"
        :data="deliverySummaryItems"
        border
        size="small"
        style="margin-top: 16px"
      >
        <el-table-column prop="name" label="物資" />
        <el-table-column label="配送數量" width="160">
          <template #default="{ row }"> {{ row.qty }}{{ row.unit }} </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="deliveryConfirmVisible = false">返回修改</el-button>
        <el-button
          type="primary"
          :loading="submitting.delivery"
          @click="submitDelivery"
        >
          送出
        </el-button>
      </template>
    </el-dialog>

    <!-- Deliver All Confirm -->
    <el-dialog
      v-model="deliverAllConfirmVisible"
      title="確認全部送達"
      class="dialog-responsive dialog-confirm"
    >
      <el-descriptions v-if="deliveryTarget" border :column="1" size="small">
        <el-descriptions-item label="配送到">
          {{ deliveryTarget.org }}
        </el-descriptions-item>
        <el-descriptions-item label="地址">
          {{ deliveryTarget.address }}
        </el-descriptions-item>
      </el-descriptions>

      <el-table
        v-if="deliverAllSummaryItems.length > 0"
        :data="deliverAllSummaryItems"
        border
        size="small"
        style="margin-top: 16px"
      >
        <el-table-column prop="name" label="物資" />
        <el-table-column label="尚缺數量" width="160">
          <template #default="{ row }">
            {{ row.remain }}{{ row.unit }}
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="deliverAllConfirmVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting.delivery"
          @click="submitDeliverAll"
        >
          確認全部送達
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import {
  ArrowDown,
  Clock,
  Location,
  Phone,
  Plus,
  TopRight,
  Van,
  WarningFilled,
} from "@element-plus/icons-vue";

const USE_NEW_API = true;
const API_BASE_URL = USE_NEW_API
  ? "https://api.gf250923.org"
  : "https://guangfu250923.pttapp.cc";

const TYPE_MAP = {
  "食物/水": { label: "飲食", order: 0, color: "#14b8a6" },
  醫療用品: { label: "醫療用品", order: 1, color: "#f59e0b" },
  生活用品: { label: "生活用品", order: 2, color: "#22c55e" },
  大型機具: { label: "大型機具", order: 3, color: "#3b82f6" },
  動物醫療: { label: "動物醫療", order: 4, color: "#934f36" },
  水電: { label: "水電", order: 5, color: "#8b5cf6" },
  其他: { label: "其他", order: 6, color: "#a855f7" },
};

const typeOptions = Object.keys(TYPE_MAP).map((value) => ({
  value,
  label: TYPE_MAP[value].label,
}));

const requests = ref([]);
const loading = ref(false);
const loadingMore = ref(false);
const nextPageUrl = ref(null);
const totalItems = ref(0);
const supplyProviders = reactive({});
const providersLoading = new Set();
const loadMoreTrigger = ref(null);
const supportsIntersectionObserver =
  typeof window !== "undefined" && "IntersectionObserver" in window;
let infiniteObserver;

const submitting = reactive({
  create: false,
  delivery: false,
});

const selectedTag = ref("");
const showPendingOnly = ref(false);
const showFulfilledOnly = ref(false);
const tagFilterOptions = computed(() => [
  { value: "", label: "全部類別" },
  ...typeOptions,
]);
const hasMore = computed(() => Boolean(nextPageUrl.value));

const createDialogVisible = ref(false);
const createConfirmVisible = ref(false);
const createPolicyAccepted = ref(false);
const completedCollapsed = reactive({});
const fulfilledCollapsed = reactive({});
const deliveryDialogVisible = ref(false);
const deliveryConfirmVisible = ref(false);
const deliverAllConfirmVisible = ref(false);

const createForm = reactive({
  org: "",
  phone: "",
  address: "",
  items: [],
});

const deliveryTarget = ref(null);
const deliveryPicks = reactive({});

const makeEmptyItem = () => ({
  type: "",
  name: "",
  need: 1,
  unit: "",
  got: 0,
});

const resetCreateForm = () => {
  createForm.org = "";
  createForm.phone = "";
  createForm.address = "";
  createForm.items.splice(0, createForm.items.length, makeEmptyItem());
  createPolicyAccepted.value = false;
};

const addCreateItem = () => {
  createForm.items.push(makeEmptyItem());
};

const removeCreateItem = (index) => {
  if (createForm.items.length <= 1) return;
  createForm.items.splice(index, 1);
};

const openCreate = () => {
  resetCreateForm();
  createDialogVisible.value = true;
};

const onCreateClosed = () => {
  createConfirmVisible.value = false;
  createPolicyAccepted.value = false;
};

const sanitizeItem = (item) => ({
  type: item.type,
  name: item.name?.trim() ?? "",
  need: Number.isFinite(Number(item.need)) ? Number(item.need) : 0,
  unit: item.unit?.trim() ?? "",
  got: Number.isFinite(Number(item.got)) ? Number(item.got) : 0,
});

const createItems = computed(() =>
  createForm.items.map((item) => sanitizeItem(item))
);

const createPayload = computed(() => ({
  org: createForm.org.trim(),
  phone: createForm.phone.trim(),
  address: createForm.address.trim(),
  items: createItems.value,
}));

const isCreateValid = computed(() => {
  const payload = createPayload.value;
  if (!payload.org || !payload.address) return false;
  if (payload.items.length === 0) return false;
  if (!createPolicyAccepted.value) return false;
  return payload.items.every(
    (item) => !!item.type && !!item.name && item.need >= 1 && !!item.unit
  );
});

const createSummaryItems = computed(() =>
  createPayload.value.items.map((item) => ({
    name: item.name,
    typeLabel: typeMeta(item.type).label,
    need: item.need,
    unit: item.unit,
  }))
);

const openCreateConfirm = () => {
  if (!isCreateValid.value || submitting.create) return;
  createConfirmVisible.value = true;
};

const submitCreate = async () => {
  if (!isCreateValid.value || submitting.create) return;
  submitting.create = true;
  try {
    const payload = createPayload.value;
    await createRequest(payload);
    ElMessage.success(`已新增 ${payload.items.length} 個物資需求`);
    createConfirmVisible.value = false;
    createDialogVisible.value = false;
    await fetchRequests();
  } catch (error) {
    ElMessage.error(error.message || "新增需求失敗");
  } finally {
    submitting.create = false;
  }
};

const onDeliveryClosed = () => {
  deliveryConfirmVisible.value = false;
  deliverAllConfirmVisible.value = false;
  resetDeliveryPicks();
  deliveryTarget.value = null;
};

const resetDeliveryPicks = () => {
  Object.keys(deliveryPicks).forEach((key) => delete deliveryPicks[key]);
};

const openDelivery = (req) => {
  deliveryTarget.value = req;
  resetDeliveryPicks();
  deliveryDialogVisible.value = true;
};

const deliveryDisplayItems = computed(() => {
  if (!deliveryTarget.value) return [];
  return deliveryTarget.value.items
    .map((item, index) => ({ ...item, index }))
    .filter((item) => remainingNeed(item) > 0);
});

const canConfirmDelivery = computed(() =>
  Object.values(deliveryPicks).some((qty) => qty > 0)
);

const setDeliveryPick = (index, value) => {
  if (!deliveryTarget.value) return;
  const item = deliveryTarget.value.items[index];
  if (!item) return;
  const remain = remainingNeed(item);
  const val = clampNumber(Number(value) || 0, 0, remain);
  if (val > 0) {
    deliveryPicks[index] = val;
  } else {
    delete deliveryPicks[index];
  }
};

const deliverySummaryItems = computed(() => {
  if (!deliveryTarget.value) return [];
  return Object.entries(deliveryPicks)
    .filter(([, qty]) => qty > 0)
    .map(([idx, qty]) => {
      const index = Number(idx);
      const item = deliveryTarget.value.items[index];
      return {
        index,
        name: item?.name ?? "",
        unit: item?.unit ?? "",
        qty,
      };
    });
});

const deliverAllSummaryItems = computed(() => {
  if (!deliveryTarget.value) return [];
  return deliveryTarget.value.items
    .map((item, index) => ({ ...item, index, remain: remainingNeed(item) }))
    .filter((item) => item.remain > 0)
    .map((item) => ({
      index: item.index,
      name: item.name,
      remain: item.remain,
      unit: item.unit,
    }));
});

const openDeliveryConfirm = () => {
  if (!canConfirmDelivery.value || submitting.delivery) return;
  deliveryConfirmVisible.value = true;
};

const submitDelivery = async () => {
  if (!deliveryTarget.value || submitting.delivery) return;
  const summary = deliverySummaryItems.value;
  if (summary.length === 0) return;
  submitting.delivery = true;
  try {
    const deliveryData = {};
    summary.forEach((item) => {
      const original = deliveryTarget.value.items[item.index];
      const remain = remainingNeed(original);
      const newGot = Math.min(
        original.need,
        (original.got ?? 0) + Math.min(item.qty, remain)
      );
      deliveryData[item.index] = newGot;
    });
    await updateDeliveryProgress(deliveryTarget.value.id, deliveryData);
    ElMessage.success("已提交配送");
    deliveryConfirmVisible.value = false;
    deliveryDialogVisible.value = false;
    await fetchRequests();
  } catch (error) {
    ElMessage.error(error.message || "配送更新失敗");
  } finally {
    submitting.delivery = false;
  }
};

const openDeliverAllConfirm = () => {
  if (!deliveryTarget.value) return;
  if (deliverAllSummaryItems.value.length === 0) {
    ElMessage.info("此需求已全部完成");
    return;
  }
  deliverAllConfirmVisible.value = true;
};

const submitDeliverAll = async () => {
  if (!deliveryTarget.value || submitting.delivery) return;
  const summary = deliverAllSummaryItems.value;
  if (summary.length === 0) return;
  submitting.delivery = true;
  try {
    const deliveryData = {};
    summary.forEach((item) => {
      deliveryData[item.index] = deliveryTarget.value.items[item.index].need;
    });
    await updateDeliveryProgress(deliveryTarget.value.id, deliveryData);
    ElMessage.success("已標記全部送達");
    deliverAllConfirmVisible.value = false;
    deliveryDialogVisible.value = false;
    await fetchRequests();
  } catch (error) {
    ElMessage.error(error.message || "配送更新失敗");
  } finally {
    submitting.delivery = false;
  }
};

const mergedRequests = computed(() => {
  const merged = mergeRequestsByOrganization(requests.value);
  return merged.sort((a, b) => {
    const aCompleted = isCompleted(a);
    const bCompleted = isCompleted(b);
    if (aCompleted && !bCompleted) return 1;
    if (!aCompleted && bCompleted) return -1;
    return 0;
  });
});

const visibleRequests = computed(() => {
  let list = mergedRequests.value;
  if (selectedTag.value) {
    list = list.filter((req) =>
      req.items.some((item) => item.type === selectedTag.value)
    );
  }

  // filtering for checkboxes
  if (showPendingOnly.value) {
    list = list.filter((req) => requestStatus(req).label !== "已完成");
  } else if (showFulfilledOnly.value) {
    list = list.filter((req) => requestStatus(req).label === "已完成");
  } else if (hasMore.value || loadingMore.value) {
    // both checkboxes are off
    // show unfinished requests only, until the pages are completely loaded
    list = list.filter((req) => requestStatus(req).label !== "已完成");
  }

  return list;
});

const cardTags = (req) => {
  const metas = [...new Set(req.items.map((item) => typeMeta(item.type)))];
  return metas
    .sort((a, b) => a.order - b.order)
    .map((meta) => ({
      label: meta.label,
      value: meta.label,
      color: meta.color,
    }));
};

const cardClasses = (req) => ({
  "is-completed": isCompleted(req),
  "has-medical": req.items.some((item) => item.type === "醫療用品"),
  "is-collapsed": isCompletedCollapsed(req),
});

const displayPhone = (req) => {
  if (isCompleted(req)) return "";
  return req.phone ?? "";
};

const phoneHref = (phone) => {
  if (!phone) return "";
  const sanitized = `${phone}`.replace(/[^0-9+#*]/g, "");
  return `tel:${sanitized || phone}`;
};

const requestStatus = (req) => {
  if (isCompleted(req)) return { label: "已完成", type: "success" };
  if (
    req.items.some(
      (item) => item.type === "醫療用品" && remainingNeed(item) > 0
    )
  ) {
    return { label: "緊急", type: "danger" };
  }
  if (req.items.some((item) => remainingNeed(item) > 0)) {
    return { label: "尚缺", type: "warning" };
  }
  return { label: "緊急", type: "danger" };
};

const isCompleted = (req) =>
  req.items.every((item) => (item.got ?? 0) >= (item.need ?? 0));

const typeMeta = (type) => TYPE_MAP[type] ?? TYPE_MAP["其他"];

const remainingNeed = (item) => Math.max(0, (item.need ?? 0) - (item.got ?? 0));

const decorateRequestItems = (req) =>
  req.items.map((item, index) => ({
    item,
    index,
    remaining: remainingNeed(item),
  }));

const pendingItems = (req) =>
  decorateRequestItems(req).filter(({ remaining }) => remaining > 0);

const fulfilledItems = (req) =>
  decorateRequestItems(req).filter(({ remaining }) => remaining === 0);

const stationsForRequest = (req) => {
  if (!req?.items?.length) return [];
  const itemById = new Map(
    req.items.filter((item) => item?.id).map((item) => [item.id, item])
  );
  const providersMap = new Map();
  req.items.forEach((item) => {
    if (!item?.id) return;
    const providers = supplyProviders[item.id] || [];
    providers.forEach((provider) => {
      const normalizedName = (provider.name || "").trim().toLowerCase();
      const fallbackKey = `${provider.address || ""}|${
        provider.phone || ""
      }`.trim();
      const key =
        normalizedName ||
        provider.id ||
        fallbackKey ||
        `${item.id}-${provider.name || ""}`;
      if (!providersMap.has(key)) {
        providersMap.set(key, {
          id: provider.id || key,
          name: provider.name?.trim() || "未命名物資站",
          address: (provider.address || "").trim(),
          phone: (provider.phone || "").trim(),
          supplies: new Map(),
        });
      }
      const entry = providersMap.get(key);
      if (!entry.id && provider.id) entry.id = provider.id;
      if ((!entry.name || entry.name === "未命名物資站") && provider.name) {
        entry.name = provider.name.trim();
      }
      if (!entry.address && provider.address) {
        entry.address = provider.address.trim();
      }
      if (!entry.phone && provider.phone) {
        entry.phone = provider.phone.trim();
      }
      const supplyId = provider.supplyItemId || item.id;
      const matchedItem = itemById.get(supplyId) || item;
      const supplyName = matchedItem?.name || item.name || "未命名物資";
      const supplyKey = supplyId || `${item.id}-${supplyName}`;
      const supplyUnitRaw =
        provider.provideUnit ?? matchedItem?.unit ?? item.unit ?? "";
      const supplyUnit =
        typeof supplyUnitRaw === "string"
          ? supplyUnitRaw.trim()
          : `${supplyUnitRaw}`.trim();
      const supplyCount =
        provider.provideCount !== null && provider.provideCount !== undefined
          ? provider.provideCount
          : null;
      const existingSupply = entry.supplies.get(supplyKey);
      if (existingSupply) {
        if (
          (existingSupply.count === null ||
            existingSupply.count === undefined) &&
          supplyCount !== null
        ) {
          existingSupply.count = supplyCount;
          existingSupply.unit = supplyUnit;
        }
      } else {
        entry.supplies.set(supplyKey, {
          id: supplyKey,
          name: supplyName,
          count: supplyCount,
          unit: supplyUnit,
        });
      }
    });
  });
  return Array.from(providersMap.values()).map((provider) => ({
    ...provider,
    address: provider.address || "地址未提供",
    supplies: Array.from(provider.supplies.values()),
  }));
};

const isItemFulfilled = (item) => remainingNeed(item) === 0;

const progressPercentage = (item) => {
  if (!item.need || item.need <= 0) return 0;
  return Math.round(
    Math.max(0, Math.min(100, ((item.got ?? 0) / item.need) * 100))
  );
};

const itemProgressStatus = (item) => {
  if (remainingNeed(item) === 0) return "success";
  return "exception";
};

const isFulfilledCollapsed = (req) => {
  if (!fulfilledItems(req).length) return true;
  const state = fulfilledCollapsed[req.id];
  return state === undefined ? true : state;
};

const toggleFulfilledCollapse = (req) => {
  if (!fulfilledItems(req).length) return;
  fulfilledCollapsed[req.id] = !isFulfilledCollapsed(req);
};

const syncCompletedCollapseState = (list = mergedRequests.value) => {
  list.forEach((req) => {
    if (isCompleted(req)) {
      if (completedCollapsed[req.id] === undefined) {
        completedCollapsed[req.id] = true;
      }
    } else if (completedCollapsed[req.id] !== undefined) {
      delete completedCollapsed[req.id];
    }
  });
};

const syncFulfilledCollapseState = (list = mergedRequests.value) => {
  list.forEach((req) => {
    if (fulfilledItems(req).length > 0) {
      if (fulfilledCollapsed[req.id] === undefined) {
        fulfilledCollapsed[req.id] = true;
      }
    } else if (fulfilledCollapsed[req.id] !== undefined) {
      delete fulfilledCollapsed[req.id];
    }
  });
};

const isCompletedCollapsed = (req) => {
  if (!isCompleted(req)) return false;
  const state = completedCollapsed[req.id];
  return state === undefined ? true : state;
};

const toggleCompletedCollapse = (req) => {
  if (!isCompleted(req)) return;
  completedCollapsed[req.id] = !isCompletedCollapsed(req);
};

const handleCardClick = (req) => {
  if (!isCompleted(req)) return;
  toggleCompletedCollapse(req);
};

const formatTimeAgo = (timestamp) => {
  if (!timestamp) return "時間未知";
  const now = Math.floor(Date.now() / 1000);
  const diff = now - timestamp;
  if (diff < 0) return "剛剛";
  if (diff < 60) return "剛剛";
  if (diff < 3600) return `${Math.floor(diff / 60)}分鐘前`;
  const hours = Math.floor(diff / 3600);
  if (hours < 24) return `${hours}小時前`;
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  if (days < 7) {
    return remainingHours === 0
      ? `${days}天前`
      : `${days}天${remainingHours}小時前`;
  }
  const weeks = Math.floor(days / 7);
  const remainingDays = days % 7;
  if (weeks < 4) {
    return remainingDays === 0
      ? `${weeks}週前`
      : `${weeks}週${remainingDays}天前`;
  }
  const months = Math.floor(days / 30);
  const remainingWeeks = Math.floor((days % 30) / 7);
  if (months < 12) {
    return remainingWeeks === 0
      ? `${months}個月前`
      : `${months}個月${remainingWeeks}週前`;
  }
  const years = Math.floor(days / 365);
  const remainingMonths = Math.floor((days % 365) / 30);
  return remainingMonths === 0
    ? `${years}年前`
    : `${years}年${remainingMonths}個月前`;
};

const mapLink = (address) =>
  `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    address
  )}`;

const clampNumber = (value, min, max) => {
  const num = Number.isFinite(value) ? value : Number(value);
  if (!Number.isFinite(num)) return min;
  return Math.max(min, Math.min(max, num));
};

const transformApiData = (apiData) =>
  apiData.map((item) => ({
    id: item.id,
    org: item.name || "未命名單位",
    address: item.address || "地址未提供",
    phone: item.phone || "",
    contact: item.contact || "",
    status: item.status || "active",
    needed_people: item.needed_people || 1,
    notes: item.notes || "",
    lng: item.lng || 0,
    lat: item.lat || 0,
    map_link: item.map_link || "",
    created_at: item.created_at || Math.floor(Date.now() / 1000),
    time: item.time || 0,
    items: item.supplies
      ? item.supplies
          .filter((supply) => supply != null)
          .map((supply) => ({
            id: supply.id || "",
            name: supply.name || "未命名物資",
            type: supply.tag || "其他",
            need: supply.total_number || supply.total_count || 1,
            got: supply.received_count || supply.recieved_count || 0,
            unit: supply.unit || "個",
          }))
      : [],
  }));

const transformSupplyProviders = (providers) =>
  (Array.isArray(providers) ? providers : [])
    .filter(
      (provider) => provider != null && !isNeedIgnoreNote(provider.notes ?? "")
    )
    .map((provider, index) => ({
      id: provider.id || `provider-${index}`,
      name: provider.name || "未命名物資站",
      phone: provider.phone || "",
      address: provider.address || "地址未提供",
      note: provider.notes || "",
      supplyItemId: provider.supply_item_id || "",
      provideCount: (() => {
        const value =
          provider.provide_count ?? provider.provideCount ?? provider.count;
        if (value === null || value === undefined || value === "") return null;
        const num = Number(value);
        return Number.isFinite(num) ? num : null;
      })(),
      provideUnit: (() => {
        const value =
          provider.provide_unit ?? provider.provideUnit ?? provider.unit ?? "";
        if (value === null || value === undefined) return "";
        return typeof value === "string" ? value.trim() : `${value}`.trim();
      })(),
    }));

const parseSupplyProvidersResponse = (data) => {
  if (!data) return [];
  if (
    (!data["@type"] || data["@type"] === "Collection") &&
    Array.isArray(data.member)
  ) {
    return transformSupplyProviders(data.member);
  }
  if (Array.isArray(data)) {
    return transformSupplyProviders(data);
  }
  return transformSupplyProviders([data]);
};

const fetchSupplyProviders = async (supplyItemId) => {
  if (!supplyItemId) return [];
  const cached = supplyProviders[supplyItemId];
  if (cached !== undefined) return cached;
  if (providersLoading.has(supplyItemId)) return [];
  providersLoading.add(supplyItemId);
  try {
    const url = `${API_BASE_URL}/supply_providers?supply_item_id=${encodeURIComponent(
      supplyItemId
    )}`;
    const response = await fetch(url);
    if (!response.ok) {
      if (response.status === 404) {
        supplyProviders[supplyItemId] = [];
        return [];
      }
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const providers = parseSupplyProvidersResponse(data);
    supplyProviders[supplyItemId] = providers;
    if (typeof window !== "undefined") {
      requestAnimationFrame(adjustGoogleSitesHeight);
    }
    return providers;
  } catch (error) {
    ElMessage.warning(`無法載入物資站資訊: ${error.message}`);
    supplyProviders[supplyItemId] = [];
    if (typeof window !== "undefined") {
      requestAnimationFrame(adjustGoogleSitesHeight);
    }
    return [];
  } finally {
    providersLoading.delete(supplyItemId);
  }
};

const ensureProvidersForRequests = async (list) => {
  const supplyIds = new Set();
  list.forEach((req) => {
    if (isCompleted(req)) return;
    (req.items || []).forEach((item) => {
      if (remainingNeed(item) === 0) return;
      if (item?.id) supplyIds.add(item.id);
    });
  });
  const idsToFetch = Array.from(supplyIds).filter(
    (id) => id && supplyProviders[id] === undefined
  );
  if (idsToFetch.length === 0) return;
  await Promise.all(idsToFetch.map((id) => fetchSupplyProviders(id)));
};

const mergeRequestsByOrganization = (list) => {
  const mergedMap = new Map();
  list.forEach((req) => {
    const key = `${req.org}|${req.address}|${req.phone}`;
    const itemsWithSupplyId = req.items.map((item) => ({
      ...item,
      supplyId: req.id,
    }));
    if (mergedMap.has(key)) {
      const existing = mergedMap.get(key);
      existing.items.push(...itemsWithSupplyId);
      if (req.created_at > existing.created_at) {
        existing.created_at = req.created_at;
      }
    } else {
      mergedMap.set(key, {
        ...req,
        items: itemsWithSupplyId,
      });
    }
  });
  return Array.from(mergedMap.values());
};

const transformToApiData = (frontendData) => {
  if (frontendData.items.length === 0) {
    throw new Error("至少需要一個物資項目");
  }

  const ret = {
    name: frontendData.org,
    address: frontendData.address,
    phone: frontendData.phone,
    supplies: {
      tag: frontendData.items[0].type,
      name: frontendData.items[0].name,
      unit: frontendData.items[0].unit,
    },
  };

  if (USE_NEW_API) {
    ret.supplies.received_count = frontendData.items[0].got;
    ret.supplies.total_number = frontendData.items[0].need;
  } else {
    ret.supplies.recieved_count = frontendData.items[0].got;
    ret.supplies.total_count = frontendData.items[0].need;
  }

  return ret;
};

const isNeedIgnoreNote = (value) => {
  if (value === null || value === undefined) return false;
  const normalized = `${value}`.trim().toLowerCase();
  return (
    normalized === "test" ||
    normalized === "測試" ||
    normalized === "need_delete"
  );
};

const parseApiResponse = (data) => {
  if (!data) {
    return {
      items: [],
      next: null,
      previous: null,
      totalItems: 0,
      limit: 0,
      offset: 0,
    };
  }
  if (
    (!data["@type"] || data["@type"] === "Collection") &&
    Array.isArray(data.member)
  ) {
    return {
      items: transformApiData(data.member),
      next: data.next ?? null,
      previous: data.previous ?? null,
      totalItems: data.totalItems ?? data.member.length ?? 0,
      limit: data.limit ?? 0,
      offset: data.offset ?? 0,
    };
  }
  if (Array.isArray(data)) {
    return {
      items: transformApiData(data),
      next: null,
      previous: null,
      totalItems: data.length,
      limit: data.length,
      offset: 0,
    };
  }
  return {
    items: transformApiData([data]),
    next: null,
    previous: null,
    totalItems: 1,
    limit: 1,
    offset: 0,
  };
};

const normalizeNextUrl = (url) => {
  if (!url) return null;
  return /^https?:/i.test(url) ? url : `${API_BASE_URL}${url}`;
};

const fetchRequests = async ({ append = false } = {}) => {
  if (loading.value || loadingMore.value) return;

  const baseUrl = USE_NEW_API
    ? `${API_BASE_URL}/supplies?limit=50&offset=0`
    : `${API_BASE_URL}/supplies?embed=all&limit=50&offset=0`;
  const targetUrl = append ? normalizeNextUrl(nextPageUrl.value) : baseUrl;

  if (!targetUrl) return;

  if (append) {
    loadingMore.value = true;
  } else {
    loading.value = true;
  }

  try {
    const response = await fetch(targetUrl);
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status} - ${errorText}`);
    }
    const data = await response.json();
    const parsed = parseApiResponse(data);
    const mergedItems = append
      ? [...requests.value, ...parsed.items]
      : parsed.items;
    const deduped = [];
    const seen = new Set();
    mergedItems.forEach((item) => {
      if (!item?.id || !seen.has(item.id)) {
        if (item?.id) seen.add(item.id);
        deduped.push(item);
      }
    });
    requests.value = deduped;

    // Disable the supply provider query as no one would write the data currently
    // await ensureProvidersForRequests(deduped);

    nextPageUrl.value = normalizeNextUrl(parsed.next);
    totalItems.value = Math.max(
      parsed.totalItems ?? deduped.length,
      deduped.length
    );
    syncCompletedCollapseState();
    syncFulfilledCollapseState();
  } catch (error) {
    const message = append ? "無法載入更多資料" : "無法載入需求資料";
    ElMessage.error(`${message}: ${error.message}`);
  } finally {
    if (append) {
      loadingMore.value = false;
    } else {
      loading.value = false;
    }
    requestAnimationFrame(adjustGoogleSitesHeight);
  }
};

const createRequest = async (payload) => {
  // First, create the supply with the first item
  const firstItemData = transformToApiData({
    ...payload,
    items: [payload.items[0]],
  });
  const firstResponse = await fetch(`${API_BASE_URL}/supplies`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(firstItemData),
  });

  if (!firstResponse.ok) {
    const errorText = await firstResponse.text();
    throw new Error(
      `第 1 個物資新增失敗: HTTP ${firstResponse.status} - ${errorText}`
    );
  }

  const firstResponseData = await firstResponse.json();
  const supplyId = firstResponseData.id;
  const valid_pin = firstResponseData.valid_pin ?? "";

  if (!supplyId) {
    throw new Error("無法取得物資 ID");
  }

  // Then create the remaining items using the supply_id
  if (payload.items.length > 1) {
    const remainingItems = payload.items.slice(1);
    const promises = remainingItems.map((item) => {
      const supplyItemData = {
        supply_id: supplyId,
        tag: item.type,
        name: item.name,
        unit: item.unit,
      };

      if (USE_NEW_API) {
        supplyItemData.total_number = item.need;
        supplyItemData.valid_pin = valid_pin;
      } else {
        supplyItemData.total_count = item.need;
      }

      return fetch(`${API_BASE_URL}/supply_items`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(supplyItemData),
      });
    });

    const responses = await Promise.all(promises);
    for (let i = 0; i < responses.length; i += 1) {
      const response = responses[i];
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `第 ${i + 2} 個物資新增失敗: HTTP ${response.status} - ${errorText}`
        );
      }
    }
  }
};

const updateDeliveryProgress = async (requestId, deliveryData) => {
  const merged = mergeRequestsByOrganization(requests.value);
  const req = merged.find((item) => item.id === requestId);
  if (!req) {
    throw new Error("找不到指定的需求");
  }
  const deliveryBySupply = {};
  Object.entries(deliveryData).forEach(([indexStr, newGot]) => {
    const index = Number(indexStr);
    const item = req.items[index];
    if (!item) return;
    const supplyId = item.supplyId || requestId;
    if (!deliveryBySupply[supplyId]) {
      deliveryBySupply[supplyId] = [];
    }
    const count = newGot - (item.got ?? 0);
    if (count > 0) {
      deliveryBySupply[supplyId].push({ id: item.id, count });
    }
  });
  const promises = Object.entries(deliveryBySupply).map(([supplyId, items]) =>
    fetch(`${API_BASE_URL}/supplies/${supplyId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(items),
    })
  );
  const responses = await Promise.all(promises);
  for (let i = 0; i < responses.length; i += 1) {
    const response = responses[i];
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`配送失敗: HTTP ${response.status} - ${errorText}`);
    }
  }
};

const adjustGoogleSitesHeight = () => {
  const minHeight =
    window.innerWidth <= 480 ? 500 : window.innerWidth <= 768 ? 600 : 800;
  document.documentElement.style.minHeight = `${minHeight}px`;
  document.body.style.minHeight = `${minHeight}px`;
};

const loadMoreRequests = () => {
  if (!hasMore.value || loading.value || loadingMore.value) return;
  fetchRequests({ append: true });
};

const ensureObserver = () => {
  if (!supportsIntersectionObserver) return null;
  if (infiniteObserver) return infiniteObserver;
  infiniteObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          loadMoreRequests();
        }
      });
    },
    {
      root: null,
      rootMargin: "256px 0px",
      threshold: 0.01,
    }
  );
  return infiniteObserver;
};

const teardownObserver = () => {
  if (!infiniteObserver) return;
  infiniteObserver.disconnect();
  infiniteObserver = null;
};

onMounted(() => {
  fetchRequests();
  adjustGoogleSitesHeight();
  window.addEventListener("resize", adjustGoogleSitesHeight);
  ensureObserver();
});

onUnmounted(() => {
  window.removeEventListener("resize", adjustGoogleSitesHeight);
  teardownObserver();
});

watch(mergedRequests, () => {
  const list = mergedRequests.value;
  syncCompletedCollapseState(list);
  syncFulfilledCollapseState(list);
  requestAnimationFrame(adjustGoogleSitesHeight);
});

watch(selectedTag, () => {
  requestAnimationFrame(adjustGoogleSitesHeight);
});

watch(showPendingOnly, () => {
  if (showPendingOnly.value) {
    showFulfilledOnly.value = !showPendingOnly.value;
  }
  requestAnimationFrame(adjustGoogleSitesHeight);
});

watch(showFulfilledOnly, () => {
  if (showFulfilledOnly.value) {
    showPendingOnly.value = !showFulfilledOnly.value;
  }
  requestAnimationFrame(adjustGoogleSitesHeight);
});

watch(
  () => loadMoreTrigger.value,
  (el, prev) => {
    const observer = ensureObserver();
    if (!observer) return;
    if (prev) observer.unobserve(prev);
    if (el && hasMore.value) {
      observer.observe(el);
    }
  },
  { flush: "post" }
);

watch(hasMore, (value) => {
  const observer = ensureObserver();
  if (!observer) return;
  const target = loadMoreTrigger.value;
  if (!target) return;
  if (value) {
    observer.observe(target);
  } else {
    observer.unobserve(target);
  }
});
</script>

<style scoped>
html {
  font-size: 20px;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  flex-direction: column;
  flex-wrap: wrap;
  gap: 12px;
  padding: 24px;
  border-radius: 0 0 24px 24px;
  background-color: #20314b;
  width: 100%;
  box-sizing: border-box;
}

.header-main {
  width: 100%;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.outter-header {
  background: #20314b;
  color: #fff;
  padding: 12px 20px;
  font-weight: 500;
  text-align: center;
  cursor: default;
  width: 100%;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #fff;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.tag-filter {
  min-width: 160px;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
}

.header-note {
  align-items: flex-start;
  gap: 8px;
  font-size: 0.9rem;
  color: #f87171;
  font-weight: 500;
  text-align: left;
}

.outline-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: 1px solid currentColor;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
  line-height: 1;
}

.create-btn-icon {
  margin-right: 8px;
}

.header-note .note-icon {
  flex-shrink: 0;
  font-size: 12px;
  width: 16px;
  height: 16px;
  align-self: center;
  justify-self: center;
}

.page-main {
  flex: 1;
  padding: 0 24px 24px;
}

.list-controls {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 48px;
  max-width: 720px;
  margin: 0 auto 16px;
}

.list-controls .tag-filter {
  min-width: 200px;
}

.pending-checkbox {
  margin: 0;
  white-space: nowrap;
}

.loading {
  margin-top: 48px;
}

.loading-placeholder,
.loading-more {
  max-width: 520px;
  margin: 32px auto 0;
}

.no-more {
  text-align: center;
  color: #64748b;
  margin: 24px 0 48px;
  font-size: 0.95rem;
}

.infinite-scroll-trigger {
  width: 100%;
  height: 1px;
}

.load-more-fallback {
  display: flex;
  justify-content: center;
  margin: 24px 0 48px;
}

.cards-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px;
  max-width: 720px;
  margin: 0 auto;
}

.request-card {
  position: relative;
  overflow: visible;
  border-radius: 18px;
  min-height: 100%;
}

.request-card.has-medical {
  border: 2px solid rgba(239, 68, 68, 0.35);
}

.request-card.is-completed.has-medical {
  border: 2px solid rgba(239, 68, 68, 0.35);
}

.request-card.is-completed {
  background: #e2e8f0;
  border: 1px solid #cbd5f5;
  cursor: default;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.card-title h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.published-at {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #6b7280;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

:deep(.el-tag) {
  border: none;
}

.meta-text {
  margin-left: 6px;
}

.muted {
  color: #6b7280;
}

.card-contact {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-main {
  display: flex;
  flex-direction: column;
  background: transparent;
}

.card-main.is-clickable {
  cursor: pointer;
}

.card-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border-radius: 30px;
}

.request-card.is-completed :deep(.el-card__footer) {
  padding: 0;
}

.card-footer.is-clickable {
  cursor: pointer;
}

.completed-toggle {
  display: flex;
  justify-content: center;
  margin-top: 4px;
}

.completed-toggle-btn {
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: transparent;
  border-color: transparent;
  box-shadow: none;
}

.completed-toggle-btn .el-icon {
  font-size: 18px;
  color: #334155;
  transition: transform 0.2s ease, color 0.2s ease;
}

.completed-toggle-btn.is-expanded .el-icon {
  transform: rotate(180deg);
}

@media (hover: hover) {
  .card-main.is-clickable:hover {
    background: #f1f5f9;
  }

  .completed-toggle-btn:hover {
    border-color: transparent;
  }

  .completed-toggle-btn:hover .el-icon,
  .request-card.is-completed:hover .completed-toggle-btn .el-icon {
    color: var(--el-color-primary);
  }
}

.section-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1f2937;
  position: relative;
}

.section-title::before {
  content: "";
  display: block;
  width: 100%;
  border-top: 1px dashed #e2e8f0;
  margin: 12px 0;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
  width: 100%;
}

.contact-row {
  display: inline-flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.9rem;
  color: #334155;
}

.contact-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-start;
  text-decoration: none;
}

.contact-link-map {
  text-decoration: underline;
  text-underline-offset: 3px;
  color: var(--el-color-primary);
}

.contact-link-map:hover {
  color: var(--el-color-primary-dark-2);
}

.contact-link-icon {
  font-size: 1rem;
  margin-top: 0 !important;
}

.contact-link-phone {
  color: #0f766e;
}

.contact-link-phone:hover {
  color: #0d9488;
}

.contact-row :deep(.el-icon) {
  line-height: 1;
  margin-top: 2px;
}

.card-content {
  margin-top: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: transparent;
}

.card-stations {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.station-scroll {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 240px;
  overflow-y: auto;
  padding-right: 4px;
}

.station-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.station-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
}

.station-name {
  font-weight: 600;
  color: #1f2937;
}

.station-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: inherit;
  justify-content: flex-start;
  text-align: left;
}

.station-link-address {
  color: var(--el-color-primary);
}

.station-link-address .station-link-text-address {
  color: inherit;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 4px;
}

.station-link-address :deep(.el-icon) {
  color: var(--el-color-primary);
}

.station-link-phone {
  color: #0f766e;
}

.station-link-phone .station-link-text-phone {
  color: inherit;
}

.station-link :deep(.el-icon) {
  font-size: 16px;
}

.station-empty {
  font-size: 0.85rem;
  color: #475569;
  border-radius: 8px;
  line-height: 1.5;
}

.station-supplies {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.station-supplies-title {
  font-size: 0.8rem;
  color: #475569;
  font-weight: 500;
  background-color: #add8bd;
  width: fit-content;
  padding: 2px 8px;
  border-radius: 6px;
}

.station-supplies-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.station-supply-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 12px;
  font-size: 0.85rem;
  color: #334155;
}

.station-supply-row + .station-supply-row {
  border-top: 1px dashed #e2e8f0;
  padding-top: 6px;
}

.supply-name {
  font-weight: 500;
}

.supply-count {
  font-weight: 600;
  white-space: nowrap;
}

.station-supplies-empty {
  font-size: 0.8rem;
  color: #94a3b8;
}

.station-note {
  font-size: 0.75rem;
  color: #475569;
  white-space: pre-wrap;
  line-height: 1.4;
}

.all-fulfilled-hint {
  font-size: 14px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 8px;
  padding: 8px 12px;
}

.fulfilled-items {
  border-top: 1px dashed #e5e7eb;
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fulfilled-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #6b7280;
  font-size: 14px;
}

.fulfilled-title {
  font-weight: 500;
}

.fulfilled-toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #0f766e;
}

.fulfilled-toggle-icon {
  transition: transform 0.2s ease;
}

.fulfilled-toggle-icon.is-open {
  transform: rotate(180deg);
}

.fulfilled-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-row + .item-row {
  border-top: 1px dashed #e5e7eb;
  padding-top: 12px;
}

.item-row.is-fulfilled {
  background: #f3f4f6;
  border-radius: 12px;
  padding: 12px;
}

.item-row.is-fulfilled + .item-row {
  border-top: none;
}

.item-row.is-fulfilled .item-name {
  color: #4b5563;
}

.item-row.is-fulfilled .item-description,
.item-row.is-fulfilled .need-number {
  color: #6b7280;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-name {
  font-weight: 600;
  font-size: 1rem;
}

.item-description {
  display: flex;
  flex-direction: column;
  font-size: 0.9rem;
  color: #4b5563;
  gap: 4px;
  width: 100%;
}

.need-number {
  color: #ef4444;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.card-stamp {
  position: absolute;
  bottom: 16px;
  right: 12px;
  transform: rotate(10deg);
  padding: 6px 32px;
  font-weight: 700;
  border: 3px solid #22c55e;
  color: #15803d;
  border-radius: 12px;
  background: rgba(34, 197, 94, 0.12);
  font-size: 1rem;
  z-index: 5;
  pointer-events: none;
}

.page-footer {
  padding: 0 24px 32px;
  text-align: center;
  color: #6b7280;
  font-size: 0.95rem;
}

.form-grid {
  display: flex;
  flex-direction: column;
}

.hint {
  display: block;
  margin-top: 4px;
  font-size: 0.8rem;
  color: #6b7280;
}

.hint.with-icon {
  display: inline-flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.4;
}

.hint.with-icon :deep(.el-icon) {
  margin-top: 2px;
  flex-shrink: 0;
}

.policy-checkbox {
  margin-top: 28px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.85rem;
  line-height: 1.4;
}

.policy-checkbox :deep(.el-checkbox__label) {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.required-icon {
  color: #ef4444;
  font-weight: 700;
}

.materials-section {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.materials-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 8px;
}

.materials-header h3 {
  margin: 0;
  font-size: 1rem;
}

.required {
  color: #ef4444;
  margin-left: 4px;
}

.items-empty {
  padding: 16px;
  background: #f9fafb;
  border: 1px dashed #d1d5db;
  border-radius: 12px;
  text-align: center;
  color: #6b7280;
}

.material-row {
  display: grid;
  grid-template-columns: 150px 1fr 120px 120px auto;
  gap: 12px;
  align-items: center;
}

.material-row > * {
  width: 100%;
}

.el-button {
  padding: 20px 24px;
  font-size: 1rem;
}

.material-row .el-button {
  justify-self: end;
}

.material-type-select,
.material-need-input,
.material-unit-input {
  width: 100%;
}

.add-item-button {
  width: 100%;
  margin-top: 4px;
}

@media (min-width: 768px) {
  .item-description {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }

  .item-description span:last-child {
    text-align: right;
    margin-right: 56px;
  }
}

@media (max-width: 768px) {
  .cards-grid {
    max-width: 100%;
  }

  .material-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .material-row .el-button {
    justify-self: flex-start;
    padding-left: 0;
  }
}

:deep(.el-dialog.dialog-responsive) {
  width: min(720px, calc(100vw - 32px));
  max-width: 100%;
}

:deep(.el-dialog.dialog-confirm) {
  width: min(520px, calc(100vw - 32px));
}

:deep(.el-dialog.dialog-confirm .el-dialog__body) {
  max-height: min(70vh, 520px);
  overflow-y: auto;
}

@media (max-width: 600px) {
  :deep(.el-dialog.dialog-responsive) {
    margin-top: 8vh;
  }

  :deep(.el-dialog.dialog-confirm) {
    margin-top: 12vh;
  }

  .deliver-card {
    padding: 14px;
  }

  .deliver-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .deliver-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 10px;
  }

  .deliver-input {
    flex: 1;
    min-width: 140px;
    max-width: 220px;
  }

  /* Mobile: add separators between materials in create modal */
  .materials-section .material-row + .material-row {
    border-top: 1px dashed #e2e8f0;
    padding-top: 12px;
  }
}

.delivery-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 8px;
}

.deliver-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fff;
}

.deliver-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.deliver-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.deliver-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-end;
  margin-left: auto;
  flex-wrap: nowrap;
}

.deliver-actions :deep(.el-button) {
  white-space: nowrap;
}

.delivery-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.deliver-input {
  width: 160px;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

@media (max-width: 640px) {
  .footer-actions {
    gap: 0;
  }
}

@media (max-width: 960px) {
  .page-header {
    border-radius: 0;
  }

  .list-controls {
    padding: 0 12px;
  }

  .material-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .list-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .list-controls .tag-filter {
    width: 100%;
  }

  .pending-checkbox {
    align-self: flex-start;
  }

  .page-header {
    padding: 16px;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .header-right {
    align-items: flex-start;
  }

  .page-main {
    padding: 0;
  }

  .list-controls {
    max-width: 100%;
    margin: 0 0 16px;
    padding: 0 32px;
    box-sizing: border-box;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    width: 100%;
    padding: 0 12px;
    box-sizing: border-box;
  }

  .material-row {
    gap: 8px;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .tag-filter {
    width: 100%;
  }

  .header-right .el-button {
    width: 100%;
  }
}

.request-card.is-completed .card-main,
.request-card.is-completed .card-header,
.request-card.is-completed .card-header-top,
.request-card.is-completed .card-body,
.request-card.is-completed .card-content,
.request-card.is-completed .card-footer,
.request-card.is-completed .card-contact,
.request-card.is-completed .item-row,
.request-card.is-completed .card-actions {
  background: #e2e8f0;
}
</style>
