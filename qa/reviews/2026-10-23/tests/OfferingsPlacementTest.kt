package com.revenuecat.purchases.kmp.models

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertSame

class OfferingsPlacementTest {
    private val current = offering("current")
    private val selected = offering("selected")

    @Test
    fun placementLookupUsesTheSuppliedIdentifier() {
        var observed: String? = null
        val offerings = Offerings(mapOf("current" to current), current) { identifier ->
            observed = identifier
            selected
        }
        assertSame(selected, offerings.getCurrentOfferingForPlacement("onboarding"))
        assertEquals("onboarding", observed)
        assertSame(current, offerings.current)
    }

    @Test
    fun absentPlacementDoesNotFallBackToCurrentOffering() {
        val offerings = Offerings(mapOf("current" to current), current) { null }
        assertNull(offerings.getCurrentOfferingForPlacement("disabled"))
        assertSame(current, offerings.current)
    }

    @Test
    fun legacyConstructorHasNoPlacementMapping() {
        val offerings = Offerings(mapOf("current" to current), current)
        assertNull(offerings.getCurrentOfferingForPlacement("onboarding"))
        assertSame(current, offerings.getOffering("current"))
    }

    @Test
    fun identifierLookupIsIndependentOfPlacementLookup() {
        var placementCalls = 0
        val offerings = Offerings(mapOf("current" to current), current) {
            placementCalls++
            selected
        }
        assertSame(current, offerings["current"])
        assertNull(offerings.getOffering("missing"))
        assertEquals(0, placementCalls)
    }

    private fun offering(id: String): Offering = object : Offering {
        override val identifier = id
        override val serverDescription = id
        override val metadata = emptyMap<String, Any>()
        override val availablePackages = emptyList<Package>()
        override val lifetime: Package? = null
        override val annual: Package? = null
        override val sixMonth: Package? = null
        override val threeMonth: Package? = null
        override val twoMonth: Package? = null
        override val monthly: Package? = null
        override val weekly: Package? = null
        override val webCheckoutUrl: String? = null
    }
}
