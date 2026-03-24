<template>
    <ComPanel title="Connected Business Sources" :viewAll="true" class="sys-date h-17rem md:h-full ">
        <template #viewAll>
            <div class="panel-header justify-content-end">
                <a href="#" class="view-all">View All Channels</a> 
            </div>
        </template>

        <div class="panel p-4"> 
            <div class="cards"> 
                <!-- Booking.com -->
                <div class="card">
                    <div class="card-top">
                        <div class="logo-wrap logo-booking">
                            <div class="logo-icon">B</div>
                        </div>
                        <div class="source-info">
                            <div class="source-name">Booking.com</div>
                            <div class="badge up">
                                <svg viewBox="0 0 10 10">
                                    <path d="M5 2L9 7H1L5 2Z" fill="currentColor" />
                                </svg>
                                +12.5%
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="label">Total Bookings</div>
                        <div class="value">142</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:100%"></div>
                        </div>
                    </div>
                </div> 
                <!-- Expedia -->
                <div class="card">
                    <div class="card-top">
                        <div class="logo-wrap logo-expedia">
                            <div class="logo-icon">E</div>
                        </div>
                        <div class="source-info">
                            <div class="source-name">Expedia</div>
                            <div class="badge down">
                                <svg viewBox="0 0 10 10">
                                    <path d="M5 8L1 3H9L5 8Z" fill="currentColor" />
                                </svg>
                                −2.4%
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="label">Total Bookings</div>
                        <div class="value">98</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:69%"></div>
                        </div>
                    </div>
                </div>

                <!-- Airbnb -->
                <div class="card">
                    <div class="card-top">
                        <div class="logo-wrap logo-airbnb">
                            <div class="logo-icon">A</div>
                        </div>
                        <div class="source-info">
                            <div class="source-name">Airbnb</div>
                            <div class="badge up">
                                <svg viewBox="0 0 10 10">
                                    <path d="M5 2L9 7H1L5 2Z" fill="currentColor" />
                                </svg>
                                +24.8%
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="label">Total Bookings</div>
                        <div class="value">64</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:45%"></div>
                        </div>
                    </div>
                </div>

                <!-- Agoda -->
                <div class="card">
                    <div class="card-top">
                        <div class="logo-wrap logo-agoda">
                            <div class="logo-icon">A</div>
                        </div>
                        <div class="source-info">
                            <div class="source-name">Agoda</div>
                            <div class="badge up">
                                <svg viewBox="0 0 10 10">
                                    <path d="M5 2L9 7H1L5 2Z" fill="currentColor" />
                                </svg>
                                +5.2%
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="label">Total Bookings</div>
                        <div class="value">45</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:32%"></div>
                        </div>
                    </div>
                </div>

                <!-- Direct Website -->
                <div class="card">
                    <div class="card-top">
                        <div class="logo-wrap logo-direct">
                            <div class="logo-icon">W</div>
                        </div>
                        <div class="source-info">
                            <div class="source-name">Direct Website</div>
                            <div class="badge up">
                                <svg viewBox="0 0 10 10">
                                    <path d="M5 2L9 7H1L5 2Z" fill="currentColor" />
                                </svg>
                                +8.1%
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="label">Total Bookings</div>
                        <div class="value">32</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:22%"></div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </ComPanel>
</template>
<style scoped>
:root {
    --bg: #f0f2f8;
    --card-bg: #ffffff;
    --text-primary: #0f1117;
    --text-secondary: #7c8394;
    --text-muted: #adb3c1;
    --green: #16c784;
    --red: #ea3943;
    --accent: #4f6ef7;
    --border: rgba(0, 0, 0, 0.06);
    --shadow: 0 2px 12px rgba(15, 17, 23, 0.07), 0 1px 3px rgba(15, 17, 23, 0.04);
    --shadow-hover: 0 12px 40px rgba(15, 17, 23, 0.12), 0 2px 8px rgba(15, 17, 23, 0.06);
}

.panel {
    background: var(--card-bg);
    border-radius: 20px; 
    box-shadow: var(--shadow); 
    width: 100%;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.6rem;
}

.panel-title {
    font-family: inherit;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.view-all {
    font-family: inherit;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    transition: gap 0.2s ease;
}

.view-all:hover {
    gap: 0.5rem;
}

.view-all::after {
    content: '›';
    font-size: 1rem;
    line-height: 1;
}

.cards {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
}

.card {
    background: #fafbfd;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.2rem 1.3rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
    cursor: default;
    animation: fadeSlideUp 0.5s ease both;
}

.card:nth-child(1) {
    animation-delay: 0.05s;
}

.card:nth-child(2) {
    animation-delay: 0.10s;
}

.card:nth-child(3) {
    animation-delay: 0.15s;
}

.card:nth-child(4) {
    animation-delay: 0.20s;
}

.card:nth-child(5) {
    animation-delay: 0.25s;
}

@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(14px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
    background: #fff;
}

.card-top {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.2rem;
}

.logo-wrap {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.logo-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* Fallback gradient logos */
.logo-booking {
    background: linear-gradient(135deg, #003580 0%, #0057b8 100%);
}

.logo-expedia {
    background: linear-gradient(135deg, #1a1a6e 0%, #ffcc00 100%);
}

.logo-airbnb {
    background: linear-gradient(135deg, #ff5a5f 0%, #ff385c 100%);
}

.logo-agoda {
    background: linear-gradient(135deg, #5392d9 0%, #1a4fa0 100%);
}

.logo-direct {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
}

.logo-icon {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    font-family: inherit;
}

.source-info {
    flex: 1;
    min-width: 0;
}

.source-name {
    font-family: inherit;
    font-weight: 700;
    font-size: 0.88rem;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: -0.01em;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.2rem;
    font-size: 0.72rem;
    font-weight: 500;
    margin-top: 0.2rem;
    padding: 2px 6px;
    border-radius: 6px;
}

.badge.up {
    color: var(--green);
    background: rgba(22, 199, 132, 0.1);
}

.badge.down {
    color: var(--red);
    background: rgba(234, 57, 67, 0.1);
}

.badge svg {
    width: 9px;
    height: 9px;
}

.card-body {
    border-top: 1px solid var(--border);
    padding-top: 1rem;
}

.label {
    font-size: 0.68rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}

.value {
    font-family: inherit;
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.8rem;
}

.bar-track {
    height: 4px;
    background: #e8eaf0;
    border-radius: 999px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #4f6ef7, #818cf8);
    transform-origin: left;
    animation: barGrow 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.card:nth-child(1) .bar-fill {
    animation-delay: 0.2s;
}

.card:nth-child(2) .bar-fill {
    animation-delay: 0.25s;
}

.card:nth-child(3) .bar-fill {
    animation-delay: 0.30s;
}

.card:nth-child(4) .bar-fill {
    animation-delay: 0.35s;
}

.card:nth-child(5) .bar-fill {
    animation-delay: 0.40s;
}

@keyframes barGrow {
    from {
        transform: scaleX(0);
    }

    to {
        transform: scaleX(1);
    }
}

/* Subtle corner accent */
.card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 60px;
    height: 60px;
    background: radial-gradient(circle at top right, rgba(79, 110, 247, 0.06), transparent 70%);
    pointer-events: none;
}

@media (max-width: 860px) {
    .cards {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 560px) {
    .cards {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>