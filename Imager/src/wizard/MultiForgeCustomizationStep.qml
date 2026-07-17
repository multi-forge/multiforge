/*
 * SPDX-License-Identifier: Apache-2.0
 * Copyright (C) 2026 MultiForge
 */

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../qmlcomponents"
import "components"

import RpiImager

WizardStepBase {
    id: root

    title: qsTr("Customisation: MultiForge Modules")
    subtitle: qsTr("Configure optional modules to provision after the device first connects to the network.")
    showSkipButton: true
    nextButtonEnabled: true
    backButtonEnabled: true
    nextButtonAccessibleDescription: qsTr("Save module configurations and continue")
    backButtonAccessibleDescription: qsTr("Return to previous step")
    skipButtonAccessibleDescription: qsTr("Skip module provisioning and proceed to writing")

    readonly property bool scrapingAvailable: wizardContainer.forgeScrapingAvailable
    readonly property bool nonailAvailable: wizardContainer.forgeNoNailAvailable
    readonly property bool minaAvailable: wizardContainer.forgeMinaAvailable

    function refreshFocusOrder() {
        root.requestFocusRebuild()
    }

    Component.onCompleted: {
        root.registerFocusGroup("forge_options", function() {
            var items = []
            if (scrapingAvailable) {
                items.push(chkScraping.focusItem)
                if (chkScraping.checked) {
                    items.push(fieldScrapingPort)
                    items.push(fieldScrapingDataSourceUrl)
                }
            }
            if (nonailAvailable) {
                items.push(chkNoNail.focusItem)
                if (chkNoNail.checked) {
                    items.push(fieldNoNailProvider)
                    items.push(fieldNoNailModel)
                    items.push(fieldNoNailApiKey)
                }
            }
            if (minaAvailable) {
                items.push(chkMina.focusItem)
            }
            return items
        }, 0)
    }

    content: [
        ScrollView {
            id: scrollArea
            anchors.fill: parent
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            rightPadding: Style.spacingMedium

            ColumnLayout {
                width: scrollArea.availableWidth
                spacing: Style.stepContentSpacing

                WizardSectionContainer {
                    visible: root.scrapingAvailable

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Style.spacingMedium

                        ImOptionPill {
                            id: chkScraping
                            Layout.fillWidth: true
                            text: qsTr("Provision Academic Scraping API")
                            accessibleDescription: qsTr("Installs the Docker Compose academic data service after the target reaches the network.")
                            checked: false
                            onCheckedChanged: root.refreshFocusOrder()
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            visible: chkScraping.checked
                            leftPadding: Style.spacingLarge
                            spacing: Style.spacingMedium

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingMedium

                                WizardFormLabel { text: qsTr("API port:") }

                                ImTextField {
                                    id: fieldScrapingPort
                                    text: "8000"
                                    Layout.preferredWidth: 150
                                    placeholderText: qsTr("1024-65535")
                                    validator: IntValidator { bottom: 1024; top: 65535 }
                                    Accessible.description: qsTr("Port exposed by the Academic Scraping API. Choose a value from 1024 to 65535.")
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingMedium

                                WizardFormLabel { text: qsTr("Data source URL:") }

                                ImTextField {
                                    id: fieldScrapingDataSourceUrl
                                    text: "https://api.open-meteo.com/v1"
                                    Layout.fillWidth: true
                                    placeholderText: qsTr("https://example.org/api")
                                    Accessible.description: qsTr("HTTPS base URL used by the academic data collector.")
                                }
                            }
                        }
                    }
                }

                WizardSectionContainer {
                    visible: root.nonailAvailable

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Style.spacingMedium

                        ImOptionPill {
                            id: chkNoNail
                            Layout.fillWidth: true
                            text: qsTr("Provision NoNail AI Agent")
                            accessibleDescription: qsTr("Installs the NoNail command-line and MCP agent after the target reaches the network.")
                            checked: false
                            onCheckedChanged: root.refreshFocusOrder()
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            visible: chkNoNail.checked
                            leftPadding: Style.spacingLarge
                            spacing: Style.spacingMedium

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingMedium

                                WizardFormLabel { text: qsTr("LLM provider:") }

                                ImTextField {
                                    id: fieldNoNailProvider
                                    text: "anthropic"
                                    Layout.fillWidth: true
                                    placeholderText: qsTr("anthropic, openai, groq, or gemini")
                                    Accessible.description: qsTr("Provider used by NoNail. Supported values are anthropic, openai, groq, and gemini.")
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingMedium

                                WizardFormLabel { text: qsTr("Default model:") }

                                ImTextField {
                                    id: fieldNoNailModel
                                    text: "claude-sonnet-4-20250514"
                                    Layout.fillWidth: true
                                    Accessible.description: qsTr("Model identifier supplied to the configured NoNail provider.")
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingMedium

                                WizardFormLabel { text: qsTr("Provider API key:") }

                                ImTextField {
                                    id: fieldNoNailApiKey
                                    placeholderText: qsTr("Optional; leave blank to configure later")
                                    echoMode: TextInput.Password
                                    Layout.fillWidth: true
                                    Accessible.description: qsTr("Optional API key stored only on the provisioned target. It is never saved by MultiForge Imager.")
                                }
                            }
                        }
                    }
                }

                WizardSectionContainer {
                    visible: root.minaAvailable

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Style.spacingMedium

                        ImOptionPill {
                            id: chkMina
                            Layout.fillWidth: true
                            text: qsTr("Provision Mina Voice Assistant")
                            accessibleDescription: qsTr("Installs Mina and configures it to start automatically on graphical login after provisioning completes.")
                            checked: false
                            onCheckedChanged: root.refreshFocusOrder()
                        }
                    }
                }
            }
        }
    ]

    onNextClicked: {
        var settings = wizardContainer.customizationSettings

        settings.forgeScrapingEnabled = scrapingAvailable && chkScraping.checked
        wizardContainer.forgeScrapingEnabled = settings.forgeScrapingEnabled
        if (settings.forgeScrapingEnabled) {
            settings.forgeScrapingPort = fieldScrapingPort.text.trim()
            settings.forgeScrapingDataSourceUrl = fieldScrapingDataSourceUrl.text.trim()
        } else {
            delete settings.forgeScrapingPort
            delete settings.forgeScrapingDataSourceUrl
        }

        settings.forgeNoNailEnabled = nonailAvailable && chkNoNail.checked
        wizardContainer.forgeNoNailEnabled = settings.forgeNoNailEnabled
        if (settings.forgeNoNailEnabled) {
            settings.forgeNoNailProvider = fieldNoNailProvider.text.trim().toLowerCase()
            settings.forgeNoNailModel = fieldNoNailModel.text.trim()
            settings.forgeNoNailApiKey = fieldNoNailApiKey.text.trim()
        } else {
            delete settings.forgeNoNailProvider
            delete settings.forgeNoNailModel
            delete settings.forgeNoNailApiKey
        }

        settings.forgeMinaEnabled = minaAvailable && chkMina.checked
        wizardContainer.forgeMinaEnabled = settings.forgeMinaEnabled
    }

    onSkipClicked: {
        var settings = wizardContainer.customizationSettings
        delete settings.forgeScrapingEnabled
        delete settings.forgeScrapingPort
        delete settings.forgeScrapingDataSourceUrl
        delete settings.forgeNoNailEnabled
        delete settings.forgeNoNailProvider
        delete settings.forgeNoNailModel
        delete settings.forgeNoNailApiKey
        delete settings.forgeMinaEnabled

        wizardContainer.forgeScrapingEnabled = false
        wizardContainer.forgeNoNailEnabled = false
        wizardContainer.forgeMinaEnabled = false
        wizardContainer.jumpToStep(wizardContainer.stepWriting)
    }
}
