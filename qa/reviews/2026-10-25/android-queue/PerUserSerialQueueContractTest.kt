package com.revenuecat.purchases.virtualcurrencies

import org.assertj.core.api.Assertions.assertThat
import org.junit.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

class PerUserSerialQueueContractTest {
    @Test
    fun `synchronously completed queued operations retain FIFO order`() {
        val queue = PerUserSerialQueue()
        val seen = mutableListOf<Int>()
        lateinit var release: () -> Unit
        queue.enqueue("user") { release = it }
        repeat(50) { index -> queue.enqueue("user") { done -> seen.add(index); done() } }
        assertThat(seen).isEmpty()
        release()
        assertThat(seen).containsExactlyElementsOf((0 until 50).toList())
    }

    @Test
    fun `reentrant enqueue waits for its current operation`() {
        val queue = PerUserSerialQueue()
        val seen = mutableListOf<String>()
        queue.enqueue("user") { done ->
            seen.add("first start")
            queue.enqueue("user") { nextDone -> seen.add("second"); nextDone() }
            seen.add("first finish")
            done()
        }
        assertThat(seen).containsExactly("first start", "first finish", "second")
    }

    @Test
    fun `concurrent enqueue and completion execute each operation once without overlap`() {
        val queue = PerUserSerialQueue()
        val pool = Executors.newFixedThreadPool(8)
        val started = CountDownLatch(1)
        val finished = CountDownLatch(800)
        val active = AtomicInteger()
        val overlaps = AtomicInteger()
        val count = AtomicInteger()
        try {
            repeat(8) {
                pool.submit {
                    started.await()
                    repeat(100) {
                        queue.enqueue("user") { done ->
                            if (active.incrementAndGet() != 1) overlaps.incrementAndGet()
                            count.incrementAndGet()
                            active.decrementAndGet()
                            done()
                            finished.countDown()
                        }
                    }
                }
            }
            started.countDown()
            assertThat(finished.await(15, TimeUnit.SECONDS)).isTrue()
            assertThat(count.get()).isEqualTo(800)
            assertThat(overlaps.get()).isZero()
        } finally { pool.shutdownNow() }
    }
}
